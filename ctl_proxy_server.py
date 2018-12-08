import sys
import http.client
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


class ThreadingSimpleProxy(ThreadingMixIn, HTTPServer):
    pass


class ChaiTeaLatteProxy(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            url_object = urlparse(self.path)
            if url_object.path[1:].isdigit():
                size = int(url_object.path[1:])
                if size < 9999:
                    conn = http.client.HTTPConnection(url_object.netloc)
                    conn.request('GET', url_object.path)
                    res = conn.getresponse()
                    self.send_response(res.status)
                    self.send_header('Content-Type', res.getheader('Content-Type'))
                    self.send_header('Content-Size', res.getheader('Content-Size'))
                    self.end_headers()
                    self.wfile.write(res.read())
                    return

                else:
                    self.send_error(414, 'Request-URI Too Long')
                    return

            else:
                self.send_error(414, 'Request-URI Must Be Integer')
                return

        except IOError:
            self.send_error(404, "File Not Found")


PORT = 8888

server = ThreadingSimpleProxy(("localhost", PORT), ChaiTeaLatteProxy)
print("ChaiTeaLatte HTTP Server running on localhost(127.0.0.1) using port", PORT)
try:
    while 1:
        sys.stdout.flush()
        server.handle_request()
except KeyboardInterrupt:
    print("\nShutting down server per users request.")
