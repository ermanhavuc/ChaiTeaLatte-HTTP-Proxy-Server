import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


class ChaiTeaLatteHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if str(self.path[1:]).isdigit():
                size = int(self.path[1:])
                if 100 <= size <= 20000:
                    filename = str(size) + ".html"
                    content = "<html>\n<head>\n<title>"+str(size)+" Byte!</title>\n</head>\n<body>\n"
                    for x in range(0, size - 74 - len(str(size))):
                        content += "A"
                    content += "\n</body>\n</html>"
                    f = open(filename, "w")
                    f.write(content)
                    f.close()

                    f = open(filename, "rb")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Size", size)
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return

                else:
                    self.send_error(414, 'Request-URI Not Suitable')
                    return
            else:
                self.send_error(414, 'Request-URI Must Be Integer')
                return

        except IOError:
            self.send_error(404, "File Not Found")


if sys.argv[1:]:
    PORT = int(sys.argv[1])
else:
    PORT = 8080

server = ThreadingSimpleServer(("localhost", PORT), ChaiTeaLatteHandler)
print("ChaiTeaLatte HTTP Server running on localhost(127.0.0.1) using port", PORT)
try:
    while 1:
        sys.stdout.flush()
        server.handle_request()
except KeyboardInterrupt:
    print("\nShutting down server per users request.")
