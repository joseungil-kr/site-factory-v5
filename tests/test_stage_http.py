import contextlib
import functools
import http.server
import threading
import urllib.request
import urllib.error
import unittest
from pathlib import Path
from urllib.parse import quote
from v5.engine import build

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class LocalHTTP(unittest.TestCase):
    def test_sample_pages_serve_200_missing_page_404(self):
        build('ansan-promotion-plant')
        directory=Path(__file__).resolve().parents[1]/'dist/ansan-promotion-plant'
        handler=functools.partial(QuietHandler,directory=str(directory))
        srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        runner=threading.Thread(target=srv.serve_forever,daemon=True);runner.start()
        try:
            origin='http://127.0.0.1:'+str(srv.server_port)
            for path in ['/','/2.html','/10.html','/'+quote('견적계산기.html')]:
                with urllib.request.urlopen(origin+path,timeout=5) as r:
                    self.assertEqual(r.status,200)
                    self.assertIn('noindex,nofollow',r.read().decode('utf-8'))
            with self.assertRaises(urllib.error.HTTPError) as err:
                urllib.request.urlopen(origin+'/500.html',timeout=5)
            self.assertEqual(err.exception.code,404)
            with urllib.request.urlopen(origin+'/robots.txt',timeout=5) as r:
                self.assertIn('Disallow: /',r.read().decode('utf-8'))
        finally:
            srv.shutdown();srv.server_close();runner.join(timeout=3)

if __name__=='__main__':unittest.main()
