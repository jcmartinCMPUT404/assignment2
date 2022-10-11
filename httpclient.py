#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")


def get_remote_ip(host):
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print ('Hostname could not be resolved. Exiting')
        sys.exit()
    return remote_ip

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port=80):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def create_connection(self, url):
        parsed_url = urllib.parse.urlparse(url)
        self.host = parsed_url.hostname
        self.port = parsed_url.port if parsed_url.port else 80
        self.path = parsed_url.path if parsed_url.path else "/"
        self.connect(self.host, self.port)

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def create_get_request_header(self):
        return f"GET {self.path} HTTP/1.1\r\n" \
            f"Host: {self.host}\r\n" \
            f"Connection: Close\r\n\r\n"

    def create_post_request_header(self):
        return f"POST {self.path} HTTP/1.1\r\n" \
            f"Host: {self.host}\r\n" \
            f"Content-Type: application/x-www-form-urlencoded\r\n" \
            f"Content-Length: {len(self.content)}\r\n" \
            f"Connection: Close\r\n\r\n" \
            f"{self.content}\r\n"

    def send_and_process_response(self, get):
        if get:
            self.sendall(self.create_get_request_header())
        else:
            self.sendall(self.create_post_request_header())
        server_response = self.recvall(self.socket)
        self.close();
        self.code = int(server_response.split()[1])
        self.body = server_response.split("\r\n\r\n")[1]
        print(server_response)

    def GET(self, url, args=None):
        self.create_connection(url)      
        self.send_and_process_response(1)  
        return HTTPResponse(self.code, self.body)

    def POST(self, url, args=None):
        self.create_connection(url)
        self.content = urllib.parse.urlencode(args) if args else ''
        self.send_and_process_response(0)  
        return HTTPResponse(self.code, self.body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

