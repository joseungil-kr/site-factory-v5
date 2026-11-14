const HOSTS = Object.freeze({
  "clinicflower.nalmada.net": "clinicflower",
  "clinicopen.nalmada.net": "clinicopen",
  "clinicpresent.nalmada.net": "clinicpresent"
});
const IMAGES = new Set(['hero.webp','hospital.webp','dental.webp','oriental.webp','phone.webp']);
const HEADERS={'X-Robots-Tag':'noindex, nofollow, noarchive','X-Content-Type-Options':'nosniff','Cache-Control':'no-store','Referrer-Policy':'strict-origin-when-cross-origin'};
function denied(status=404){return new Response('Not found',{status,headers:HEADERS});}
export default {
  async fetch(request, env){
    if(request.method!=='GET'&&request.method!=='HEAD')return denied(405);
    const url=new URL(request.url);
    const site=Object.prototype.hasOwnProperty.call(HOSTS,url.hostname)?HOSTS[url.hostname]:null;
    if(!site)return denied();
    let dest;
    if(url.pathname==='/' || url.pathname==='/index.html')dest='/sites/'+site+'/index.html';
    else if(url.pathname==='/robots.txt')return new Response(request.method==='HEAD'?null:'User-agent: *\nDisallow: /\n',{status:200,headers:{...HEADERS,'Content-Type':'text/plain; charset=utf-8'}});
    else if(url.pathname==='/assets/style.css')dest=url.pathname;
    else if(url.pathname.startsWith('/assets/images/')&&IMAGES.has(url.pathname.slice(15)))dest=url.pathname;
    else return denied();
    url.pathname=dest;
    url.search='';
    const result=await env.ASSETS.fetch(new Request(url, {method:request.method}));
    const headers=new Headers(result.headers);
    for(const [k,v] of Object.entries(HEADERS))headers.set(k,v);
    return new Response(request.method==='HEAD'?null:result.body,{status:result.status,headers});
  }
};