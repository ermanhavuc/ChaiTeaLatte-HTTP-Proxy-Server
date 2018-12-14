import socket
import sys
import os
import datetime
from _thread import *
import threading


lock = threading.Lock()


def create_headers_errors(status, filetype, size):
    headers = ''
    content = ''
    if status == 200:
        headers = "HTTP/1.1 200 OK\r\n"
    elif status == 400:
        headers = "HTTP/1.1 400 Bad Request\r\n"
        content = "400 Bad Request"
        size = len(content)
    elif status == 501:
        headers = "HTTP/1.1 501 Not Implemented\r\n"
        content = "501 Not Implemented"
        size = len(content)
    elif status == 404:
        headers = "HTTP/1.1 404 Not Found\r\n"
        content = "404 Not Found"
        size = len(content)

    headers += "Date: %s\r\n" % datetime.datetime.now()
    headers += "Server: ChaiTeaLatteHTTPServer/1.0\r\n"
    headers += "Content-Length: %d\r\n" % size
    headers += "Content-Type: %s\r\n" % filetype

    if status == 200:
        return headers + "\r\n"
    else:
        return headers + "\r\n" + content


def create_response(request):
    req_parts = request.split(' ')
    req_message = req_parts[0]
    req_uri = req_parts[1][1:]
    data = ''
    filetype = "text/html"

    if req_message == 'GET':
        if req_uri.isdigit():
            size = int(req_uri)
            if 100 <= size <= 20000:
                w_size = size - 74 - len(str(size))
                content = "<html>\n<head>\n<title>" + str(size) + " Byte!</title>\n</head>\n<body>\n"
                if os.path.isfile("ctl"):
                    ctl_size = os.path.getsize("ctl")
                    if ctl_size < w_size:
                        ctl_f = open("ctl", "r")
                        ctl = ctl_f.read()
                        ctl_f.close()
                        content += ctl
                        for i in range(0, w_size - ctl_size + 93):
                            content += ' '
                    elif size < 150:
                        for i in range(0, w_size + 7):
                            content += 'A'
                    else:
                        recipe = "<h2>To load Chai Tea Latte Recipe, at least 2479 bytes needed!</h2>"
                        content += recipe[0:w_size]
                        for i in range(0, w_size - len(recipe) + 7):
                            content += ' '
                else:
                    for i in range(0, w_size):
                        content += "A"
                content += "\n</body>\n</html>"
                data = create_headers_errors(200, filetype, len(content)) + content
        else:
            data = create_headers_errors(400, filetype, 0)
    else:
        data = create_headers_errors(501, filetype, 0)
    return data


def server_thread(cc):

    req = cc.recv(1024)
    print(req.decode().split('\r\n')[0])
    response = create_response(req.decode())
    print(response.split('\r\n')[0])
    cc.sendall(response.encode())
    lock.release()
    cc.close()


def Main():
    if sys.argv[1:]:
        PORT = int(sys.argv[1])
    else:
        PORT = 8080

    HOST = '127.0.0.1'

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(1)

    print("ChaiTeaLatte HTTP Server running on %s using port" % HOST, PORT)

    while True:
        client_connection, client_address = listen_socket.accept()
        lock.acquire()
        start_new_thread(server_thread, (client_connection,))


if __name__ == '__main__':
    Main()
