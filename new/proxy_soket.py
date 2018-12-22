import socket
import os
import datetime
import hashlib
from _thread import *
import threading

lock = threading.Lock() #creating thread for every request


def create_headers_errors(status, filetype, size):# creating headers and error status
    headers = ''
    content = ''
    if status == 200: #OK
        headers = "HTTP/1.1 200 OK\r\n"
    elif status == 400:  #Bad Request
        headers = "HTTP/1.1 400 Bad Request\r\n"
        content = "400 Bad Request"
        size = len(content)
    elif status == 501: #Not Implemented
        headers = "HTTP/1.1 501 Not Implemented\r\n"
        content = "501 Not Implemented"
        size = len(content)
    elif status == 404: #Not Found
        headers = "HTTP/1.1 404 Not Found\r\n"
        content = "404 Not Found"
        size = len(content)
    elif status == 414: #Request-URI Too Long
        headers = "HTTP/1.1 414 Request-URI Too Long\r\n"
        content = "414 Request-URI Too Long"
        size = len(content)

    headers += "Date: %s\r\n" % datetime.datetime.now()
    headers += "Server: ChaiTeaLatteHTTPServer/1.0\r\n"
    headers += "Content-Length: %d\r\n" % size
    headers += "Content-Type: %s\r\n" % filetype

    if status == 200: #if status is not 200 add error mesages to content
        return headers + "\r\n"
    else:
        return headers + "\r\n" + content


def  create_response(request):
    req_parts = request.split(' ')  #split request by spaces
    req_message = req_parts[0]  # get request code
    filetype = "text/html"
    if req_message == 'GET':
        req_server = req_parts[1].split('/')[2] #get domain name 
        port = int(req_server.split(':')[1]) #get port
        req_uri = req_parts[1].split('/')[3]  #get uri
        if req_uri.isdigit(): #digit check
            size = int(req_uri)
            if size < 9999: #request bounds check
                m = hashlib.md5() #select encyript type according to md5
                m.update(req_parts[1].encode()) #encyript cache name
                cache = m.hexdigest() + ".cache" #cache name
                if os.path.exists(cache): #if cache exists,open the cache and send data from cache file
                    print("Cache hit!")
                    f = open(cache, "rb")
                    content = f.read()
                    f.close()
                    data = create_headers_errors(200, filetype, len(content)) + content.decode() #create responce with cache data
                else:    #if cache doesn't exist connect with http server get data ,write to new cache file and send to client
                    print("Cache miss!")
                    request = request.replace(req_parts[1], '/'+req_uri, 1) #
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect(('127.0.0.1', 8080))
                            s.sendall(request.encode())
                            data = s.recv(10240)
                        w_data = data.decode().split("\r\n\r\n")[1]
                        f = open(cache, "wb")
                        f.write(w_data.encode())
                        f.close()
                    except:
                        data = create_headers_errors(404, filetype, 0)
            else:
                data = create_headers_errors(414, filetype, 0) #Request-URI Too Long
        else:
            data = create_headers_errors(400, filetype, 0) #Bad Request
    else:
        data = create_headers_errors(501, filetype, 0) # Not Found
    return data


def server_thread(cc):
    req = cc.recv(10240)  # 10240  byte request received
    print(req.decode().split('\r\n')[0]) #print request first row
    response = create_response(req.decode()) #create response
    if type(response) is bytes:#when cache miss,return of http server is byte 
        print(response.decode().split('\r\n')[0]) #print response first row
        cc.sendall(response) #send response to client
    else:  #when cache hit, return is string, we neet to convert string to byte to send response
        print(response.split('\r\n')[0]) 
        cc.sendall(response.encode())
    lock.release() #thread unlocked
    cc.close()  #connection closed


def Main():

    PORT = 8888
    HOST = '127.0.0.1'

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET is used for socket type IPv4 ,SOCK_STREAM is used for TCP connection
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #set socket options with reusable address the port
    listen_socket.bind((HOST, PORT))  #bind socket to port and host
    listen_socket.listen(1)#socket listen every 1 milisec.

    print("ChaiTeaLatte Proxy Server running on %s using port" % HOST, PORT)

    while True:
        client_connection, client_address = listen_socket.accept()  #when client connected to server ,return client connection object and client address
        lock.acquire()  #thread locked
        start_new_thread(server_thread, (client_connection,))  #new thread created


if __name__ == '__main__':
    Main()
