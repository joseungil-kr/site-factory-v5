/** Exact-host-only Winterbbang home indexable release.
 * The one public URL is https://winterbbang.nalmada.net/.
 * All 1,803 regional/hub pages and the workers.dev hostname stay noindex.
 * No routing, DNS, credential or HTTP submission capabilities exist here.
 */
const PUBLIC_HOST = "winterbbang.nalmada.net";
const PREVIEW_HOST = "sfv54-winterbbang-preview.joseungil.workers.dev";
const OWNERSHIP_KEY = "2a73e0239c3bcec564b34d6386cc622c";
const PUBLIC_CANONICAL = "https://" + PUBLIC_HOST + "/";
const BLACKLISTED = new Set(["/sitemap.xml", "/" + OWNERSHIP_KEY + ".txt"]);
const PREVIEW_ROBOTS = "User-agent: *\nDisallow: /\n";

function failClosed(status = 404) {
  return new Response("Not found", {
    status, headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "X-Robots-Tag": "noindex, nofollow, noarchive",
    },
  });
}

function hostOnly(request) {
  const url = new URL(request.url);
  return url.hostname.toLowerCase() === PUBLIC_HOST
    ? "public"
    : url.hostname.toLowerCase() === PREVIEW_HOST
      ? "preview"
      : "unknown";
}

export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return failClosed(405);
    }
    const role = hostOnly(request);
    if (role === "unknown") return failClosed();
    const url = new URL(request.url);
    const pathname = url.pathname;
    const home = pathname === "/" || pathname === "/index.html";

    if (role === "preview" && pathname === "/robots.txt") {
      return new Response(PREVIEW_ROBOTS, {
        status: 200,
        headers: {
          "Content-Type": "text/plain; charset=utf-8",
          "X-Robots-Tag": "noindex, nofollow, noarchive",
        },
      });
    }
    if (role === "preview" && BLACKLISTED.has(pathname)) {
      return failClosed();
    }
    if (pathname === "/") url.pathname = "/index.html";
    const response = await env.ASSETS.fetch(new Request(url, request));
    const headers = new Headers(response.headers);
    // Workers.dev is always blocked. Public domain allows only home
    // while other (human-viewable) locality pages retain noindex.
    const indexable = role === "public" && home && response.status === 200;
    if (indexable) {
      headers.delete("X-Robots-Tag");
    } else {
      headers.set("X-Robots-Tag", "noindex, nofollow, noarchive");
    }
    if (role === "preview" && home && response.status === 200) {
      // Same static assets are shared on both hostnames. Revert public
      // homepage robots/canonical on workers.dev to avoid duplicate indexing.
      let body = await response.text();
      const publicMeta = '<meta name="robots" content="index,follow">';
      if (!body.includes(publicMeta) ||
          !body.includes('<link rel="canonical" href="' + PUBLIC_CANONICAL + '">')) {
        return failClosed(503);
      }
      body = body.replace(publicMeta, '<meta name="robots" content="noindex,nofollow">');
      body = body.replace('<link rel="canonical" href="' + PUBLIC_CANONICAL + '">', "");
      headers.delete("Content-Length");
      headers.delete("ETag");
      return new Response(body, { status: 200, headers });
    }
    // Host-specific key and sitemap are served by the shared static asset
    // directory only on the public hostname. They never appear on preview.
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};

export { PUBLIC_HOST, PREVIEW_HOST, OWNERSHIP_KEY };
