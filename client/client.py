import socket
import threading
import os
import sys
import argparse


class MyException(Exception):
    pass
class Client(object):
    def __init__(
        self, 
        hostname,
        server_host='192.168.2.189', 
        server_port=7734, 
        upload_port=None,

    ):
        self.server_host = server_host
        self.server_port = server_port
        
        self.upload_port = upload_port
        self.hostname = hostname
        
    def start(self):
        print('Start connecting to the server on %s:%s' % (self.server_host, self.server_port))
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            if(not self.hostname):
                raise Exception('Hostname is empty')
            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            self.server.connect((self.server_host, self.server_port))
            
        except Exception as e:
            print(e)
            self.shutdown()
            
        cli_thread = threading.Thread(target=self.cli)
        cli_thread.start()
        
        self.set_client_name()
        
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
       
    def set_client_name(self):
        try:            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            message = 'SET_CLIENT_NAME\n' + self.hostname
            self.server.sendall(message.encode())
        except Exception as e:
            print(e)
            self.shutdown()
            
        
            
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
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--hostname', dest='hostname', type=str, help='Server host name')
    
    args = parser.parse_args()
    
    client = Client(hostname=args.hostname)
    
    client.start()