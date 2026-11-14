/** Winterbbang full 1,804-URL public candidate.
 * Exact public host only: index/follow + self canonical for real HTML pages.
 * Exact workers.dev host: noindex/nofollow all 1,804 HTML and 404.
 * Preview robots disallow; sitemap/ownership key only on public hostname.
 * This Worker does not change DNS, routes, credentials or IndexNow state.
 */
const PUBLIC_HOST = "winterbbang.nalmada.net";
const PREVIEW_HOST = "sfv54-winterbbang-preview.joseungil.workers.dev";
const INDEXNOW_KEY = "2a73e0239c3bcec564b34d6386cc622c";
const PUBLIC_ORIGIN = "https://" + PUBLIC_HOST;
const KEY_ROUTE = "/" + INDEXNOW_KEY + ".txt";
const HIDE_ON_PREVIEW = new Set(["/sitemap.xml", KEY_ROUTE]);
const PREVIEW_ROBOTS = "User-agent: *\nDisallow: /\n";
const INDEX_META = '<meta name="robots" content="index,follow">';
const NOINDEX_META = '<meta name="robots" content="noindex,nofollow">';

function blocked(status=404) {
  return new Response("Not found", {
    status,
    headers: {
      "Content-Type":"text/plain; charset=utf-8",
      "X-Robots-Tag":"noindex, nofollow, noarchive",
    },
  });
}
function hostRole(request) {
  const host = new URL(request.url).hostname.toLowerCase();
  if (host === PUBLIC_HOST) return "public";
  if (host === PREVIEW_HOST) return "preview";
  return null;
}
function isHTML(pathname) {
  return pathname === "/" || pathname.endsWith(".html");
}
function stripPublicSEO(body) {
  if (!body.includes(INDEX_META)) {
    throw new Error("Generated public HTML missing index,follow meta");
  }
  const canonical = /<link rel="canonical" href="https:\/\/winterbbang\.nalmada\.net\/[^"]*">/g;
  const matches = [...body.matchAll(canonical)];
  if (matches.length !== 1) {
    throw new Error("Generated public HTML missing unique public canonical");
  }
  return body.replace(INDEX_META,NOINDEX_META).replace(canonical,"");
}
export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") return blocked(405);
    const role = hostRole(request);
    if (role === null) return blocked(404);
    const url = new URL(request.url);
    const path = url.pathname;
    if (role === "preview" && path === "/robots.txt") {
      return new Response(PREVIEW_ROBOTS,{
        status:200,
        headers:{
          "Content-Type":"text/plain; charset=utf-8",
          "X-Robots-Tag":"noindex, nofollow, noarchive",
        },
      });
    }
    if (role === "preview" && HIDE_ON_PREVIEW.has(path)) return blocked(404);
    if (path === "/") url.pathname = "/index.html";
    const original = await env.ASSETS.fetch(new Request(url,request));
    const headers = new Headers(original.headers);
    const ok = original.status === 200;
    const publicHTML = role === "public" && ok && isHTML(path);
    if (role === "preview" || !ok) {
      headers.set("X-Robots-Tag","noindex, nofollow, noarchive");
    } else {
      headers.delete("X-Robots-Tag");
    }
    if (role === "preview" && ok && isHTML(path) && request.method === "GET") {
      let transformed;
      try {
        transformed = stripPublicSEO(await original.text());
      } catch (_) {
        return blocked(503);
      }
      headers.delete("Content-Length");
      headers.delete("ETag");
      return new Response(transformed,{status:200,headers});
    }
    // In particular the PUBLIC Worker makes no redirects to the preview host
    // or other commercial domains. All 1,804 useful HTML pages are self-hosted.
    return new Response(original.body, {
      status:original.status,
      statusText:original.statusText,
      headers,
    });
  },
};
export { PUBLIC_HOST, PREVIEW_HOST, INDEXNOW_KEY, stripPublicSEO };
