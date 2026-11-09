import { chromium } from 'playwright';
import fs from 'node:fs';
const pageNames=(process.env.WORKER6_PAGES || 'index,2,3,4').split(',');
import path from 'node:path';
const root='reports/promotion-gift-plants';
const screenshots=path.join(root,'screenshots');
fs.mkdirSync(screenshots,{recursive:true});
const browser=await chromium.launch({headless:true});
const checks=[];
let failures=[];
for(const page of pageNames){
  for(const width of [390,1440]){
    const ctx=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
    const tab=await ctx.newPage();
    const errors=[];
    const failed=[];
    tab.on('pageerror',err=>errors.push(err.message));
    tab.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
    tab.on('response',resp=>{if(resp.url().startsWith('http://127.0.0.1:8765/') && resp.status()>=400)failed.push(resp.url()+' '+resp.status());});
    const url='http://127.0.0.1:8765/'+(page==='index'?'':page+'.html');
    const response=await tab.goto(url,{waitUntil:'networkidle'});
    await tab.evaluate(()=>document.fonts.ready);
    const result=await tab.evaluate(()=>{
      const h=document.documentElement;
      const title=document.querySelector('h1');
      const css=[...document.styleSheets].filter(x=>x.href).map(x=>x.href);
      const images=[...document.images].map(x=>({src:x.currentSrc,loaded:x.complete&&x.naturalWidth>0}));
      const body=getComputedStyle(document.body);
      return {title:title?.innerText,bodyFont:body.fontFamily,bodyFontSize:body.fontSize,bodyColor:body.color,bodyBackground:body.backgroundColor,css,images,scrollWidth:h.scrollWidth,clientWidth:h.clientWidth,overflow:h.scrollWidth>h.clientWidth+1,fontCheck:document.fonts.check('16px "Noto Sans CJK KR"'),fontStatus:document.fonts.status};
    });
    await tab.screenshot({path:path.join(screenshots,page+'-'+width+'-full.png'),fullPage:true});
    const row={page,width,status:response?.status(),...result,consoleErrors:errors,failedResponses:failed};
    checks.push(row);
    if(row.status!==200||row.overflow||row.css.length<1||row.consoleErrors.length||row.failedResponses.length||row.images.some(i=>!i.loaded)||!row.fontCheck||row.fontStatus!=='loaded')failures.push(row);
    await ctx.close();
  }
}
await browser.close();
fs.writeFileSync(path.join(root,'browser-qa.json'),JSON.stringify({checks,failures:failures.length},null,2));
console.log(JSON.stringify({checks:checks.map(({page,width,status,bodyFont,css,scrollWidth,clientWidth,overflow,fontCheck,consoleErrors,failedResponses})=>({page,width,status,bodyFont,cssCount:css.length,scrollWidth,clientWidth,overflow,fontCheck,consoleErrors,failedResponses})),failures:failures.length},null,2));
if(failures.length)process.exitCode=1;
