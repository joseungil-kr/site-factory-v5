// Skyquote exact-host public switch; all other hosts and 404 remain noindex.
// Never touch sfv5-skyquote-preview, Hallflower, WreathPrice, or third-party Worker.
const HOST='skyquote.nalmada.net';
export default {
  async fetch(request,env) {
    const u=new URL(request.url);
    const publicHost=(u.hostname===HOST&&env.SKYQUOTE_PUBLIC==='1');
    if (u.pathname==='/')u.pathname='/index.html';
    const response=await env.ASSETS.fetch(new Request(u,request));
    const headers=new Headers(response.headers);
    headers.set('X-Content-Type-Options','nosniff');
    if (!publicHost || response.status===404) {
      headers.set('X-Robots-Tag','noindex, nofollow, noarchive');
    } else {
      headers.delete('X-Robots-Tag');
    }
    return new Response(response.body,{status:response.status,headers});
  }
};
