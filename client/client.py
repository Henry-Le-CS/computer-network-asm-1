import socket
import threading
import os
import sys
import argparse

from client_helper import parse_client_cmd, parse_server_response
from pathlib import Path

class Client():
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
        
        self.is_selecting_peer = False
        self.peer_options = {}
        
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
            
        set_client_name_thread = threading.Thread(target=self.set_client_name)
        set_client_name_thread.start()

        # Wait for set_client_name to complete before starting cli
        set_client_name_thread.join()
        
        self.cli_thread = threading.Thread(target=self.cli)
        self.cli_thread.start()
                
        while True:
            try:
                data = self.server.recv(1024).decode()
                
                if data:
                    method, payload = parse_server_response(data)
                    if(method == 'print'):
                        print(data)
                        
                    elif(hasattr(self, method) and callable(getattr(self, method))):
                        getattr(self, method)(payload)
                    
            except Exception as e:
                print(e)
                break
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
                break
       
    def set_client_name(self):
        try:            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            message = 'SET_CLIENT_NAME\n' + self.hostname
            self.server.send(message.encode())
        except Exception as e:
            print(e)
            self.shutdown()
                  
    def cli(self):
        while True:
            inputStr = 'Select peer > ' if self.is_selecting_peer else '> '
            try:
                command = input(inputStr)
                
                if command == '':
                    continue
                
                method, payload = parse_client_cmd(command, self.is_selecting_peer,  self.peer_options)
                
                if hasattr(self, method) and callable(getattr(self, method)):
                    getattr(self, method)(payload)
                    
                self.is_selecting_peer = False
                self.peer_options = {}

            except Exception as e:
                print(e)
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()

    def shutdown(self, payload = None):
        print('\nShutting Down...')

        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
    def publish_file_info(self, payload):
        file_path, file_name = payload
        
        self.create_folder_if_not_exists(file_path)
        file_exists = self.check_file_exist(file_path, file_name)
        
        if not file_exists:
            print(f'File {file_name} does not exists.\n')
            return
        
        message = 'PUBLISH_FILE_INFO\n' + file_path + '\n' + file_name
        self.server.send(message.encode())
    
    def create_folder_if_not_exists(self, file_path):
        Path(file_path).mkdir(parents=True, exist_ok=True)
        
    def check_file_exist (self, file_path, file_name):
        path = file_path + '/' + file_name
        return Path(path).exists()
    
    def fetch_file_info(self, payload):
        file_name = payload
        
        message = 'FETCH_FILE_INFO\n' + file_name
        self.server.send(message.encode())

    def display_peer_options(self, payload):
        file_name, options = payload
        
        self.peer_options = {}
        
        print(f'Select peer to download file {file_name} from: \n')
        
        for i in range(len(options)):
            self.peer_options[i] = options[i]
            print(f'{i}. {options[i]}')
        
        print('\nSelect peer > ', end = '', flush=True)
        self.is_selecting_peer = True

    def download_from_peer(self, payload):
        hostname, host, port, file_path = payload
        
        print(f'\rDownloading file from {hostname}...', flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--hostname', dest='hostname', type=str, help='Server host name')
    
    args = parser.parse_args()
    
    client = Client(hostname=args.hostname, server_host='192.168.7.22')
    
    client.start()