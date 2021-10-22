#!/usr/bin/env python3

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import time
from io import StringIO

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

# if len(sys.argv)-1 != 2:
#     print(f"Usage: sys.argv[0] <port_number> <url>")
#     sys.exit()
if len(sys.argv) - 1 != 1:
    print(f"Usage: sys.argv[0] <port_number>")
    sys.exit()


class Redirect(SimpleHTTPRequestHandler):  # (BaseHTTPRequestHandler):
    def _normal_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _infinite_redirects(self):

        body = f"""
        <!doctype html>
        <html lang="da">
        <head><meta charset="utf-8">
            <title>infinite redirects</title>
        </head>
        <body>
        <p>Oh no, you fell down the rabbit hole.
        <a href="/redirect?q={time.time()}">click this link to get out!</a>
        </p>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())
        return

    def _redirect_response(self):
        self.send_response(302)
        try:
            redirect = sys.argv[2]
        except IndexError:
            redirect =  "http://localhost:64345"
        self.send_header("Location", redirect + self.path)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        # import ipdb; ipdb.set_trace()

        host = self.headers.get("host")
        print(host, self.path)
        if host.startswith("www"):
            self._redirect_response()
        elif self.path.startswith("/redirect"):
            self._infinite_redirects()
        else:
            super().do_GET()
            # self._normal_response()
            # with open(self.translate_path(self.path), 'rb') as f:
            #     self.wfile.write(f.read())

    def do_HEAD(self):

        host = self.headers.get("host")
        if host.startswith("www"):
            self._redirect_response()
        elif self.path.startswith("/redirect"):
            self._normal_response()
        else:
            super().do_HEAD()
            # self._normal_response()


HTTPServer(("", int(sys.argv[1])), Redirect).serve_forever()
