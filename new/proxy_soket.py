import socket
import os
import datetime
import hashlib
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
    elif status == 414:
        headers = "HTTP/1.1 414 Request-URI Too Long\r\n"
        content = "414 Request-URI Too Long"
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
    filetype = "text/html"
    if req_message == 'GET':
        req_server = req_parts[1].split('/')[2]
        port = int(req_server.split(':')[1])
        req_uri = req_parts[1].split('/')[3]
        if req_uri.isdigit():
            size = int(req_uri)
            if size < 9999:
                m = hashlib.md5()
                m.update(req_parts[1].encode())
                cache = m.hexdigest() + ".cache"
                if os.path.exists(cache):
                    print("Cache hit!")
                    f = open(cache, "rb")
                    content = f.read()
                    f.close()
                    data = create_headers_errors(200, filetype, len(content)) + content.decode()
                else:
                    print("Cache miss!")
                    request = request.replace(req_parts[1], '/'+req_uri, 1)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect(('127.0.0.1', port))
                        s.sendall(request.encode())
                        data = s.recv(10240)
                    w_data = data.decode().split("\r\n\r\n")[1]
                    f = open(cache, "wb")
                    f.write(w_data.encode())
                    f.close()
            else:
                data = create_headers_errors(414, filetype, 0)
        else:
            data = create_headers_errors(400, filetype, 0)
    else:
        data = create_headers_errors(404, filetype, 0)
    return data


def server_thread(cc):
    req = cc.recv(10240)
    print(req.decode().split('\r\n')[0])
    response = create_response(req.decode())
    if type(response) is bytes:
        print(response.decode().split('\r\n')[0])
        cc.sendall(response)
    else:
        print(response.split('\r\n')[0])
        cc.sendall(response.encode())
    lock.release()
    cc.close()


def Main():

    PORT = 8888
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
