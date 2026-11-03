// Public build handler; the preview entry remains unchanged.
const HOST = "webbuilder.nalmada.net";
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const publicHost = url.hostname === HOST;
    const headers = new Headers({"X-Robots-Tag": "noindex, nofollow, noarchive"});
    if (!["GET", "HEAD"].includes(request.method)) {
      headers.set("Allow", "GET, HEAD");
      return new Response("Method Not Allowed", {status: 405, headers});
    }
    if (!publicHost && ["/robots.txt", "/sitemap.xml", "/rss.xml"].includes(url.pathname)) {
      headers.set("Content-Type", "text/plain; charset=utf-8");
      return new Response(request.method === "HEAD" ? null : "User-agent: *\nDisallow: /\n",
        {status: url.pathname === "/robots.txt" ? 200 : 404, headers});
    }
    const path = url.pathname.endsWith("/") ? url.pathname + "index.html" : url.pathname;
    let result = await env.ASSETS.fetch(new Request(new URL(path, url), request));
    const missing = result.status === 404 || path === "/404.html";
    if (missing) result = await env.ASSETS.fetch(new Request(new URL("/404.html", url)));
    const h = new Headers(result.headers);
    if (publicHost && !missing && url.pathname === "/rss.xml") h.set("Content-Type", "application/rss+xml; charset=utf-8");
    h.set("X-Robots-Tag", publicHost && !missing && result.ok ? "index, follow" : "noindex, nofollow, noarchive");
    let body = result.body;
    if (!publicHost && (h.get("Content-Type") || "").includes("text/html")) {
      body = (await result.text()).replace('content="index,follow"', 'content="noindex,nofollow,noarchive"')
        .replace(/<link rel="canonical"[^>]*>/g, "")
        .replace(/<link rel="alternate" type="application\/rss\+xml"[^>]*>/g, "");
      h.delete("Content-Length");
      h.delete("ETag");
      h.set("Cache-Control", "no-store");
    }
    return new Response(request.method === "HEAD" ? null : body, {status: missing ? 404 : result.status, headers: h});
  }
};
