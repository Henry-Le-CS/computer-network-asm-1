import socket
import threading
import os
import sys
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
            print('Server is not available.')
            
        cli_thread = threading.Thread(target=self.cli)
        cli_thread.start()
        
        self.server.send('set_client_name client1'.encode('utf-8')) # Temporary set client name
        
        while True:
            try:
                data = self.server.recv(1024)
                if data:
                    print(data.decode('utf-8'))
            except Exception as e:
                print(e)
                break
            except KeyboardInterrupt:
                print('Client is shutting down...')
                self.shutdown()
                break
            
        
            
    def cli(self):
        pass
                
    def shutdown(self):
        print('\nShutting Down...')
        self.server.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    client = Client()
    
    client.start()