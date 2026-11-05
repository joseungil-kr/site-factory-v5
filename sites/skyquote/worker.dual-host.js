// Reuse the one pre-existing Skyquote preview Worker (Cloudflare Free account is at its Worker limit).
// Exact custom host may index; workers.dev stays noindex with HTML and HTTP robots in agreement.
// No API tokens, Cloudflare zone or authentication changes here.
const PUBLIC_HOST="skyquote.nalmada.net";
const ROBOTS_NOINDEX="noindex, nofollow, noarchive";
const PREVIEW_ROBOTS="User-agent: *\nDisallow: /\n";
export default {
  async fetch(request,env) {
    const incoming=new URL(request.url);
    const publicMode=incoming.hostname===PUBLIC_HOST && env.SKYQUOTE_PUBLIC==="1";
    if (!publicMode && incoming.pathname==="/robots.txt") {
      return new Response(PREVIEW_ROBOTS,{status:200,headers:{"Content-Type":"text/plain; charset=utf-8",
        "X-Robots-Tag":ROBOTS_NOINDEX,"X-Content-Type-Options":"nosniff"}});
    }
    if (!publicMode && incoming.pathname==="/sitemap.xml") {
      return new Response("Not found",{status:404,headers:{"X-Robots-Tag":ROBOTS_NOINDEX,"X-Content-Type-Options":"nosniff"}});
    }
    if (incoming.pathname==="/")incoming.pathname="/index.html";
    const original=await env.ASSETS.fetch(new Request(incoming,request));
    const headers=new Headers(original.headers);
    headers.set("X-Content-Type-Options","nosniff");
    if (!publicMode || original.status===404) {
      headers.set("X-Robots-Tag",ROBOTS_NOINDEX);
    } else {
      headers.delete("X-Robots-Tag");
    }
    const type=headers.get("Content-Type")||"";
    if (!publicMode && type.includes("text/html") && original.status===200) {
      // Render preview-specific HTML robots instead of merely overriding HTTP header.
      let html=await original.text();
      html=html.replace('<meta name="robots" content="index,follow">',
                        '<meta name="robots" content="noindex,nofollow">');
      if (!html.includes('<meta name="robots" content="noindex,nofollow">')) {
        return new Response("Unsafe preview HTML robots state",{status:503,headers:{"X-Robots-Tag":ROBOTS_NOINDEX}});
      }
      headers.delete("Content-Length");
      headers.delete("Content-Encoding");
      headers.delete("ETag");
      return new Response(html,{status:original.status,headers});
    }
    return new Response(original.body,{status:original.status,headers});
  }
};
