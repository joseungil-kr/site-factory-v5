/** Baekse city-only full release Worker.
 * Exactly baekse.nalmada.net is indexable. Its workers.dev preview is never
 * indexable and never serves the public sitemap or IndexNow ownership key.
 * Neither routes, DNS, credentials nor other Worker scripts are mutated here.
 */
const PUBLIC_HOST="baekse.nalmada.net";
const PREVIEW_HOST="sfv54-baekse-city-preview.joseungil.workers.dev";
const INDEXNOW_KEY="c4b8096fa37019ed2520a611b51da94e";
const KEY_ROUTE="/"+INDEXNOW_KEY+".txt";
const PUBLIC_ORIGIN="https://"+PUBLIC_HOST;
const META_PUBLIC='<meta name="robots" content="index,follow">';
const META_PREVIEW='<meta name="robots" content="noindex,nofollow">';
const PUBLIC_CANONICAL=/<link rel="canonical" href="https:\/\/baekse\.nalmada\.net\/[^"]*">/g;

function blocked(status=404) {
  return new Response("Not found", {
    status,
    headers:{
      "Content-Type":"text/plain; charset=utf-8",
      "X-Robots-Tag":"noindex, nofollow, noarchive"
    }
  });
}
function getRole(url) {
  const host=url.hostname.toLowerCase();
  if(host===PUBLIC_HOST)return "public";
  if(host===PREVIEW_HOST)return "preview";
  return "unknown";
}
function previewHTML(input) {
  if(!input.includes(META_PUBLIC))throw new Error("Missing public robots metadata");
  const canonicals=[...input.matchAll(PUBLIC_CANONICAL)];
  if(canonicals.length!==1)throw new Error("Expected exactly one public self canonical");
  return input.replace(META_PUBLIC,META_PREVIEW).replace(PUBLIC_CANONICAL,"");
}
export default {
  async fetch(request,env) {
    if(!["GET","HEAD"].includes(request.method))return blocked(405);
    const url=new URL(request.url);
    const role=getRole(url);
    if(role==="unknown")return blocked();
    const path=url.pathname;
    if(role==="preview"&&path==="/robots.txt") {
      return new Response("User-agent: *\nDisallow: /\n",{
        status:200,
        headers:{"Content-Type":"text/plain; charset=utf-8",
                 "X-Robots-Tag":"noindex, nofollow, noarchive"}
      });
    }
    if(role==="preview"&&(path==="/sitemap.xml"||path===KEY_ROUTE))return blocked();
    if(path==="/")url.pathname="/index.html";
    const source=await env.ASSETS.fetch(new Request(url,request));
    const headers=new Headers(source.headers);
    const isPage=path==="/"||path.endsWith(".html");
    if(role==="public"&&source.status===200) {
      headers.delete("X-Robots-Tag");
      return new Response(source.body,{status:source.status,statusText:source.statusText,headers});
    }
    headers.set("X-Robots-Tag","noindex, nofollow, noarchive");
    if(role==="preview"&&source.status===200&&isPage&&request.method==="GET") {
      let body;
      try {body=previewHTML(await source.text());}
      catch (_) {return blocked(503);}
      headers.delete("Content-Length");headers.delete("ETag");
      return new Response(body,{status:200,headers});
    }
    return new Response(source.body,{status:source.status,statusText:source.statusText,headers});
  }
};
export {PUBLIC_HOST,PREVIEW_HOST,INDEXNOW_KEY,previewHTML};
