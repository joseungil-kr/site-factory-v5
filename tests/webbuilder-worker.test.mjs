import test from "node:test";
import assert from "node:assert/strict";
import worker from "../sites/webbuilder/worker.preview.js";

const sampleEnv = {
  ASSETS: {
    async fetch(request) {
      const path = new URL(request.url).pathname;
      if (path === "/index.html") return new Response("<h1>Homepage</h1>", {
        status: 200, headers: { "Content-Type": "text/html" }
      });
      if (path === "/industry/leak/index.html") return new Response("<h1>Leak page</h1>", {
        status: 200, headers: { "Content-Type": "text/html" }
      });
      if (path === "/404.html") return new Response("<h1>Missing</h1>", {
        status: 200, headers: { "Content-Type": "text/html" }
      });
      return new Response("not found", { status: 404 });
    }
  }
};
test("workers.dev homepage is noindex regardless of hostname", async () => {
  for (const host of ["sfv55-webbuilder-preview.user.workers.dev", "webbuilder.nalmada.net"]) {
    const r = await worker.fetch(new Request("https://" + host + "/"), sampleEnv);
    assert.equal(r.status, 200);
    assert.equal(r.headers.get("X-Robots-Tag"), "noindex, nofollow, noarchive");
    assert.match(await r.text(), /Homepage/);
  }
});
test("industry trailing slash resolves to static index and stays noindex", async () => {
  const r = await worker.fetch(new Request("https://example.com/industry/leak/"), sampleEnv);
  assert.equal(r.status, 200);
  assert.match(await r.text(), /Leak page/);
  assert.match(r.headers.get("X-Robots-Tag"), /noindex/);
});
test("unknown paths return an actual 404, never 200 fallback", async () => {
  const r = await worker.fetch(new Request("https://example.com/unknown/"), sampleEnv);
  assert.equal(r.status, 404);
  assert.match(await r.text(), /Missing/);
  assert.match(r.headers.get("X-Robots-Tag"), /noindex/);
});
test("POST cannot mutate data", async () => {
  const r = await worker.fetch(new Request("https://example.com/", {method:"POST"}), sampleEnv);
  assert.equal(r.status, 405);
  assert.equal(r.headers.get("Allow"), "GET, HEAD");
  assert.match(r.headers.get("X-Robots-Tag"), /noindex/);
});
