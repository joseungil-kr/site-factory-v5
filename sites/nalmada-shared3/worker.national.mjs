/** Single authorized nalmada.net Worker for three NEW clinic subdomains only.
 * Existing unrelated nalmada.net sites remain on their existing Workers.
 * All 3 hosts serve static /sites/<site>/; the original file tree is not public.
 */
const HOSTS = Object.freeze({
  'clinicflower.nalmada.net':'clinicflower',
  'clinicopen.nalmada.net':'clinicopen',
  'clinicpresent.nalmada.net':'clinicpresent'
});
const IMAGES = new Set(['hero.webp','hospital.webp','dental.webp','oriental.webp','phone.webp','celebration-wreath.webp']);
const HEADERS = Object.freeze({'X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin'});
const blocked = (status=404) => new Response('Not found',{status,headers:{...HEADERS,'X-Robots-Tag':'noindex, nofollow, noarchive','Cache-Control':'no-store'}});
export default {
  async fetch(request, env) {
    if (!['GET','HEAD'].includes(request.method)) return blocked(405);
    const url=new URL(request.url);
    const site=Object.hasOwn(HOSTS,url.hostname)?HOSTS[url.hostname]:null;
    if (!site) return blocked(); // includes *.workers.dev and unrelated hostnames
    const path=url.pathname;
    let asset;
    if (path==='/' || path==='/index.html') asset='/sites/'+site+'/index.html';
    else if (path==='/robots.txt' || path==='/sitemap.xml' || path==='/rss.xml') asset='/sites/'+site+path;
    else if (/^\/[a-f0-9]{32}\.txt$/.test(path)) asset='/sites/'+site+path;
    else if (path==='/assets/style.css') asset=path;
    else if (path.startsWith('/assets/images/') && IMAGES.has(path.slice('/assets/images/'.length))) asset=path;
    else if (/^\/r\/\d{5}\.html$/.test(path) || /^\/[pd]\/[a-f0-9]{12}\.html$/.test(path)) asset='/sites/'+site+path;
    else return blocked();
    const at=new URL(url);
    at.pathname=asset;
    at.search='';
    const result=await env.ASSETS.fetch(new Request(at,{method:request.method}));
    const headers=new Headers(result.headers);
    for (const [key,val] of Object.entries(HEADERS)) headers.set(key,val);
    if (result.status!==200) return blocked(404);
    if (asset.endsWith('.html')) {
      headers.delete('X-Robots-Tag');
      headers.set('X-Robots-Tag','index, follow');
      headers.set('Cache-Control','public, max-age=0, must-revalidate');
    } else if (asset.endsWith('robots.txt') || asset.endsWith('sitemap.xml') || asset.endsWith('rss.xml')) {
      headers.delete('X-Robots-Tag');
      headers.set('Cache-Control','public, max-age=120');
    } else {
      headers.set('Cache-Control','public, max-age=86400');
    }
    return new Response(request.method==='HEAD'?null:result.body,{status:result.status,headers});
  }
};