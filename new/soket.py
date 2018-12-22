import socket
import sys
import os
import datetime
from _thread import *
import threading


lock = threading.Lock() #creating thread for every request


def create_headers_errors(status, filetype, size): # creating headers and error status
    headers = ''
    content = ''
    if status == 200: #OK
        headers = "HTTP/1.1 200 OK\r\n"
    elif status == 400: #Bad Request
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

    if status == 200: #if status is not 200 add error mesages to content
        return headers + "\r\n"
    else:
        return headers + "\r\n" + content


def create_response(request):
    req_parts = request.split(' ') #split request by spaces
    req_message = req_parts[0]  # get request code
    req_uri = req_parts[1][1:]
    data = ''
    filetype = "text/html"

    if req_message == 'GET':
        if req_uri.isdigit(): 
            size = int(req_uri)
            if 100 <= size <= 20000: #request bounds check
                w_size = size - 74 - len(str(size))
                content = "<html>\n<head>\n<title>" + str(size) + " Byte!</title>\n</head>\n<body>\n"
                if os.path.isfile("ctl"): #check ctl file existence to handle chai tea latte recipe
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
            data = create_headers_errors(400, filetype, 0)
    else:
        data = create_headers_errors(501, filetype, 0)
    return data


def server_thread(cc):

    req = cc.recv(1024) # 10240  byte request received
    print(req.decode().split('\r\n')[0])  #print request first row
    response = create_response(req.decode()) #create response
    print(response.split('\r\n')[0])
    cc.sendall(response.encode()) 
    lock.release() #thread unlocked
    cc.close() #connection closed
 

def Main():
    if sys.argv[1:]: #take command line argument to specify port
        PORT = int(sys.argv[1])
    else:
        PORT = 8080

    HOST = '127.0.0.1' 

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #AF_INET is used for socket type IPv4 ,SOCK_STREAM is used for TCP connection
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #set socket options with reusable address the port
    listen_socket.bind((HOST, PORT)) #bind socket to port and host
    listen_socket.listen(1) #socket listen every 1 milisec.

    print("ChaiTeaLatte HTTP Server running on %s using port" % HOST, PORT)

    while True:
        client_connection, client_address = listen_socket.accept() #when client connected to server ,return client connection object and client address
        lock.acquire() #thread locked
        start_new_thread(server_thread, (client_connection,)) #new thread created


if __name__ == '__main__':
    Main()
