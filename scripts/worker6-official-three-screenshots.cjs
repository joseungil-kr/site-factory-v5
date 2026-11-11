const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const out='reports/promotion-gift-plants/official-three-text';
 fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
 const rows=[];
 for(const file of ['index','1','2','3']){
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
   const response=await page.goto('http://127.0.0.1:8765/'+(file==='index'?'':file+'.html'));
   const result=await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,viewport:innerWidth,
      noindex:document.querySelector('meta[name="robots"]')?.content==='noindex,nofollow',
      imageCount:document.images.length,linkCount:document.querySelectorAll('a').length,
      title:document.title}));
   if(response.status()!==200||result.scrollWidth>width||!result.noindex||result.imageCount!==0)throw Error(JSON.stringify({file,width,result,status:response.status()}));
   const shot=path.join(out,'screenshots',file+'-'+width+'.png');
   await page.screenshot({path:shot,fullPage:true});
   rows.push({file,width,http:response.status(),...result,screenshot:shot});
   await page.close();
  }
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'screenshots-qa.json'),JSON.stringify(rows,null,2));
 console.log('OFFICIAL_TEXT_SCREENSHOTS_PASS',rows.length);
})().catch(e=>{console.error(e);process.exit(1)});
