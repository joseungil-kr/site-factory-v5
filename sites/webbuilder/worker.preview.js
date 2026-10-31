/** Isolated Webbuilder preview worker. Does not attach a custom domain or enable indexing. */
const ROBOTS = "noindex, nofollow, noarchive";
function protectedResponse(body, status, headers = {}) {
  const h = new Headers(headers);
  h.set("X-Robots-Tag", ROBOTS);
  h.set("Cache-Control", "no-store");
  return new Response(body, { status, headers: h });
}
export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return protectedResponse("Method Not Allowed", 405, { Allow: "GET, HEAD" });
    }
    const url = new URL(request.url);
    let assetPath = url.pathname;
    if (assetPath === "/") assetPath = "/index.html";
    else if (assetPath.endsWith("/")) assetPath += "index.html";
    const assetUrl = new URL(assetPath, url);
    const result = await env.ASSETS.fetch(new Request(assetUrl, request));
    if (result.status === 404) {
      const page404 = await env.ASSETS.fetch(new Request(new URL("/404.html", url)));
      const headBody = request.method === "HEAD" ? null : page404.body;
      return protectedResponse(headBody, 404, {
        "Content-Type": "text/html; charset=utf-8"
      });
    }
    const headers = new Headers(result.headers);
    headers.set("X-Robots-Tag", ROBOTS);
    headers.set("Cache-Control", "no-store");
    return new Response(request.method === "HEAD" ? null : result.body, {
      status: result.status, headers
    });
  }
};
