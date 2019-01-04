import sys
import http.client
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import hashlib
import os
import socket
import select


class ThreadingSimpleProxy(ThreadingMixIn, HTTPServer):
    pass


class ChaiTeaLatteProxy(BaseHTTPRequestHandler):

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i + 1:])
        else:
            host_port = netloc, 80
        print("\t" "connect to %s:%d" % host_port)
        try:
            soc.connect(host_port)
        except socket.error as arg:
            self.send_error(404, arg)
            return 0
        return 1

    def _read_write(self, soc):
        iw = [self.connection, soc]
        ow = []
        while 1:
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs:
                break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    data = i.recv(8192)
                    if data:
                        out.send(data)

    def do_CONNECT(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path, soc):
                self.log_request(200)
                self._read_write(soc)
        finally:
            soc.close()
            self.connection.close()

    def do_GET(self):
        try:
            url_object = urlparse(self.path)
            if url_object.path[1:].isdigit():
                size = int(url_object.path[1:])
                if size < 9999:
                    conn = http.client.HTTPConnection(url_object.netloc)
                    conn.request('GET', url_object.path)
                    m = hashlib.md5()
                    m.update(self.path.encode('utf-8'))
                    cache = m.hexdigest() + ".cache"
                    if os.path.exists(cache):
                        print("Cache hit!")
                        f = open(cache, "rb")
                        data = f.read()
                        self.send_response(200)
                        self.send_header('Content-Type', "text/html")
                        self.send_header('Content-Size', size)
                    else:
                        print("Cache miss!")
                        res = conn.getresponse()
                        self.send_response(res.status)
                        self.send_header('Content-Type', res.getheader('Content-Type'))
                        self.send_header('Content-Size', res.getheader('Content-Size'))
                        data = res.read()
                        f = open(cache, "wb")
                        f.write(data)
                    f.close()
                    self.end_headers()
                    self.wfile.write(data)

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
        server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server per users request.")
