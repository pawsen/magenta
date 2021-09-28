#!/usr/bin/env python3

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

"""Redirect http requests

usage
-----
./redirect <port_number> [<url>]

<port_number> is the listening port.

If <url> is specified, redirect to this url.
Otherwise redirect to http://www.localhost/

example
-------
redirect from http://localhost:64345 to http://www.localhost:64345

python redirect.py 64345 http://www.localhost:64345

HEAD -E http://localhost:64345
OR
curl -L http://localhost:64345

"""

if len(sys.argv)-1 != 2:
    print(f"Usage: sys.argv[0] <port_number> <url>")
    sys.exit()


class Redirect(SimpleHTTPRequestHandler): # (BaseHTTPRequestHandler):
    def _normal_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect_response(self):
        self.send_response(302)
        self.send_header("Location", sys.argv[2] + self.path)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        host = self.headers.get("host")
        if not "www" in host:
            self._redirect_response()
        else:
            super().do_GET()
            # self._normal_response()
            # with open(self.path, 'rb') as f:
            #     self.wfile.write(f.read())

    def do_HEAD(self):

        host = self.headers.get("host")
        if not "www" in host:
            self._redirect_response()
        else:
            super().do_HEAD()
            # self._normal_response()


HTTPServer(("", int(sys.argv[1])), Redirect).serve_forever()
