import fs from 'node:fs';
import path from 'node:path';
const dir=path.dirname(new URL(import.meta.url).pathname);
const html=fs.readFileSync(path.join(dir,'Index.html'),'utf8');
const result=html.replace(/<\?!= include\('([A-Za-z]+)'\); \?>/g,(m,n)=>fs.readFileSync(path.join(dir,n+'.html'),'utf8'));
if(result.includes('<?!='))throw new Error('Unexpanded Apps Script template');
fs.writeFileSync(path.join(dir,'demo.html'),result);
console.log('Built demo.html',result.length,'characters');
