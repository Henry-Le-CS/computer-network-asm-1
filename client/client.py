import socket
import threading
import os
import sys
import argparse
import shutil
import time
import mimetypes
import platform

from client_helper import parse_client_cmd, parse_server_response, MyException
from pathlib import Path

REPO_PATH = 'repository/'

class Client():
    def __init__(
        self, 
        controller,
        hostname='default',
        server_host='192.168.1.11', 
        server_port=7734, 
    ):
        print('a client obj init!')
        self.server_host = server_host
        self.server_port = server_port
        
        self.hostname = hostname
        
        self.is_selecting_peer = False
        self.peer_options = {}
        self.upload_port = None

        self.controller = controller

        self.remoteFiles = []
        self.peerList = []
        
    def start(self):
        """
            Start the client
        """

        print('client starting')
        if not os.path.exists(REPO_PATH):
            os.makedirs(REPO_PATH)
        
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
        
        # Maybe look into this since we have already created a thread in the App class
        # Init upload to start listening for peers, as well as setting upload port
        self.init_upload_thread = threading.Thread(target=self.init_upload)
        self.init_upload_thread.start()
        
        # Wait for the upload port to be set. Could use thread.join()
        while not self.upload_port:
            pass
        
        self.set_host_addresses()
        self.init_publish()
        print(f'Start listening for peers on port {self.upload_port}')
        
        # Start a new thread for cli
        self.cli_thread = threading.Thread(target=self.cli)
        self.cli_thread.start()
                
        while True:
            try:
                data = self.server.recv(1024).decode()
                
                if data:
                    method, payload = parse_server_response(data)
                    # If the method is print, then print the payload
                    if(method == 'print'):
                        inputStr = 'Select option > ' if self.is_selecting_peer else '> '
                        print(data + '\n' + inputStr, end = '', flush=True)
                    elif(method == 'list'):
                        print('[INFO] listing:', payload)
                    elif(method == 'list'):
                        print('[INFO] list:', payload)
                    # Else if the method is defined in the client, then call it
                    elif(hasattr(self, method) and callable(getattr(self, method))):
                        getattr(self, method)(payload)
                    
            except Exception as e:
                print(e)
                break
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
                break
       
    def set_host_addresses(self):
        try:            
            # TODO: Fetch hostname from the system, if exists then terminate the program
            message = 'SET_HOST_ADDRESSES\n' + self.hostname + '\n' + str(self.upload_port)
            self.server.send(message.encode())
        except Exception as e:
            print(e)
            self.shutdown()
                  
    def cli(self):
        while True:
            inputStr = 'Select option > ' if self.is_selecting_peer else '> '
            
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
            
    def publish_file_info(self, payload):
        file_path, file_name = payload
        print('got file path', file_path, file_name)
        
        self.create_folder_if_not_exists(file_path)
        file_exists = self.check_file_exist(file_path, file_name)
        
        if not file_exists:
            print(f'File {file_name} does not exist.\n')
            return
        
        message = 'PUBLISH_FILE_INFO\n' + file_path + '\n' + file_name + '\n' + str(self.upload_port)
        self.server.send(message.encode())
    
    def create_folder_if_not_exists(self, file_path):
        if(file_path == '.'):
            return
        
        Path(file_path).mkdir(parents=True, exist_ok=True)

    def store_file_into_repo(self, lname, fname):
        filePath = os.path.join(lname, fname)
        if not os.path.exists(filePath):
            # print('This file does not exist on your system.')
            return('File does not exist. Please try again')
        else:
            if fname in os.listdir(os.path.join(os.getcwd(), REPO_PATH)):
                return('File name already existed in repository.')
            else:
                shutil.copy(filePath, os.path.join(os.getcwd(), REPO_PATH))
                print('file stored!')

    def check_file_exist (self, file_path, file_name):
        path = file_path + '/' + file_name
        print(path)
        return Path(path).exists()
    
    # This method is run right after the connection to server is made
    def init_publish(self):
        filePath = os.path.join(os.getcwd(), REPO_PATH)
        files = []

        for file in os.listdir(filePath):
            files.append(file)

        print('[Client] pre-publishing with', files)

        message = 'INIT_PUBLISH\n' + './' + REPO_PATH + '\n' + ':'.join(files) + '\n' + str(self.upload_port)
        self.server.send(message.encode())
    
    def remove_local_file(self, payload):
        file_path, file_name = payload
        print('[Client - Delete local file] got file path', file_path, file_name)
        os.remove(os.path.join(file_path, file_name))

        message = 'REMOVE_LOCAL_FILE\n' + file_path + '\n' + file_name + '\n' + str(self.upload_port)
        self.server.send(message.encode())
    
    def fetch_file_info(self, payload):
        file_name = payload
        
        message = 'FETCH_FILE_INFO\n' + file_name
        self.server.send(message.encode())

    def display_peer_options(self, payload):
        file_name, options = payload
        
        self.peer_options = {}
        
        if(len(options) == 0):
            print(f'No peer has file {file_name}.\n> ', end = '', flush=True)
            self.is_selecting_peer = False
            return
        
        print(f'Select peer to download file {file_name} from: (example: 0)\n')
        
        for i in range(len(options)):
            self.peer_options[i] = options[i] + ' ' + file_name
            
            hostname, uploader_host, uploader_port, file_path = options[i].split()
            print(f'{i}) Hostname: {hostname}, IP: {uploader_host}, Port: {uploader_port}, File Path: {file_path}')
        
        print('\nSelect option > ', end = '', flush=True)
        self.is_selecting_peer = True

    def download_from_peer(self, payload):
        hostname, host, port, file_path, file_name = payload
        
        port = int(port)
        
        print(f'\rDownloading file {file_name} from {hostname}...\n', flush=True)
        
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            start_time = time.time()
            peer_socket.connect((host, port))

            
            message = 'DOWNLOAD_FILE\n' + file_path + '\n' + file_name
            peer_socket.send(message.encode())
            
            res_header = peer_socket.recv(1024).decode("utf-8")
            
            if res_header:
                print(res_header)
                
            path = file_path + '/' + file_name
            
            self.create_folder_if_not_exists(file_path)
            
            with open(path, 'wb') as f:
                data = peer_socket.recv(1024)
                while data:
                    f.write(data)
                    data = peer_socket.recv(1024)
                
                f.flush()
            end_time = time.time()
            
            download_time = end_time - start_time
            print(f'\rDownloaded file {file_name} from {hostname} in {download_time}s.', flush=True)
            
            peer_socket.close()
        except Exception as e:
            print(e)
            
    def init_upload(self):
        try:
            self.upload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upload_socket.bind(('', 0))

            self.upload_port = self.upload_socket.getsockname()[1]
            self.upload_socket.listen(5)
            
        except Exception as e:
            print(e)
                
        while True:
            try:
                conn, addr = self.upload_socket.accept()
                print(f'\rUpload request from {addr[0]}:{addr[1]}\n', flush=True)
                
                upload_thread = threading.Thread(target=self.upload_file, args=(conn, addr))
                upload_thread.start()
            except Exception as e:
                print(e)
                break
            except BaseException:
                print('Client is shutting down...')
                self.shutdown()
                break
        self.upload_socket.close()

    def upload_file(self, conn: socket.socket , addr):
        try:
            data = conn.recv(1024).decode("utf-8")

            if not data:
                return
            
            method, file_path, file_name = data.split()
            
            if method != 'DOWNLOAD_FILE':
                return
            
            file_exists = self.check_file_exist(file_path, file_name)
            
            if not file_exists:
                conn.send(f'File {file_name} does not exist at {file_path}'.encode())
                return
            
            path = file_path + '/' + file_name
            
            header = 'OS: %s\n' % (platform.platform())
            header += 'Content-Length: %s\n' % (os.path.getsize(path))
            header += 'Content-Type: %s\n' % (
                    mimetypes.MimeTypes().guess_type(path)[0])
            
            print('File metadata: \n' + header)
            
            conn.send(header.encode())
            try:
                print('Uploading...')

                send_length = 0
                with open(path, 'rb') as file:
                    to_send = file.read(1024)
                    
                    # Divides into packets
                    while to_send:
                        send_length += len(to_send)
                        conn.sendall(to_send)
                        to_send = file.read(1024)

                print('Uploading successfully')
                
                inputStr = 'Select option > ' if self.is_selecting_peer else '> '
                print(inputStr, end='', flush=True)
            except Exception:
                raise MyException('Uploading Failed')

                    
        except Exception as e:
            print(e)
        except BaseException:
            print('Client is shutting down...')
            self.shutdown()
        finally:
            conn.close()

    def list_peers(self, payload = None):
        message = 'FETCH_AVAILABLE_PEERS\n'
        self.server.send(message.encode())
        
    def list_files(self, payload = None):
        message = 'FETCH_ALL_FILE_INFO\n'
        self.server.send(message.encode())

    # This method is to get THE LIST of available peers as response (not as terminal's output)
    def get_available_peers(self, payload = None):
        print('[Client] sending get peers req')
        message = 'GET_ALL_AVAILABLE_PEERS\n'
        self.server.send(message.encode())

    def get_available_files(self, payload = None):
        print('[Client] sending get files req')
        message = 'GET_ALL_AVAILABLE_FILES\n'
        self.server.send(message.encode())

    def set_available_files(self, payload):
        print('setting avail files', payload)

        newlist = []

        files = payload[1:]
        for file in files:
            file_name, client_name, uploader_address = file.split(':')
            print('- ', (file_name, client_name, uploader_address), '\n')
            newlist.append((file_name, client_name, uploader_address))
        
        self.remoteFiles = newlist
        self.controller.update_FetchList()

    def make_download_request(self, payload):
        # This will call download_from_peer() method
        # payload should be:
        # - hostname, host, port, file_path, file_name = payload
        print('[Download file]')
        self.download_from_peer(payload)

    def disconnect(self):
        print('[Client] removing self')
        message = 'REMOVE_CLIENT\n' + str(self.upload_port)
        self.server.send(message.encode())

    def shutdown(self, payload = None):
        print('\nShutting Down...')
        self.disconnect()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--hostname', dest='hostname', type=str, help='Server host name')
    
    args = parser.parse_args()
    
    client = Client(hostname=args.hostname, server_host='192.168.254.144')
    
    client.start()