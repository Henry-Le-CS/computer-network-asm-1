import socket
import threading
import platform
import mimetypes
import os
import sys
import time
from pathlib import Path


class MyException(Exception):
    pass


class Client(object):
    def __init__(
        self, 
        server_host='192.168.2.189', 
        server_port=7734, 
        upload_port=None
    ):
        self.server_host = server_host
        self.server_port = server_port
        
        self.upload_port = upload_port

    def start(self):
        print('Start connecting to the server on %s:%s' % (self.server_host, self.server_port))
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.server.connect((self.server_host, self.server_port))
        except Exception as e:
            print(e)
            sys.exit(1)
        
        self.send()
        
        res = self.server.recv(1024)
        while res:
            print(res.decode())
            res = self.server.recv(1024)
            
    def send(self):
        print('Sent msg from client to server')
        
        self.server.send('Hello from client'.encode())

        
if __name__ == '__main__':
    client = Client()
    
    client.start()