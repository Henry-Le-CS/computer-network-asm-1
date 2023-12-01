import socket
import threading
import sys 
import os
import time
from server_helper import parse_server_cmd, parse_client_request

class Server:
    def __init__(
            self, 
            server_host="",
            server_port=7734,
            upload_port=None,
    ) -> None:
        self.server_host = server_host
        self.server_port = server_port
        self.upload_port = upload_port

        self.client_socket_lists = {}  # {(host, port): client}
        self.client_name_lists = {}  # {client_name: (host, port)}
        
        self.lock = threading.Lock()
        
        """
        file_references = {
            file_name: [
                ((host, port), file_path),
                ((host, port), file_path),
                ...
            ]
        }
        """
        self.file_references = {} 
        
    def start(self):
        print('Starting the server on %s:%s' % (self.server_host, self.server_port))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_host, self.server_port))
        self.server.listen(5)

        cli_thread = threading.Thread(target=self.cli)
        cli_thread.start()
        
        while True:
            try:
                client, address = self.server.accept()
                print('Client %s:%s connected.' % (address[0], address[1]))
                
                self.client_socket_lists[address] = client

                # Create thread to handle client request
                client_handler = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client, address)
                )

                client_handler.start()
            except KeyboardInterrupt:
                print('Server is shutting down...')
                self.shutdown()
                break
            
    def cli(self):
        while True:
            try:
                command = input('> ')
                
                if command == '':
                    continue
                
                method, payload = parse_server_cmd(command)
                
                if(hasattr(self, method) and callable(getattr(self, method))):
                    getattr(self, method)(payload)
                
                
            except Exception as e:
                print(e)
            except BaseException:
                self.shutdown()
    
    def set_client_name (self, payload):
        client_name, address = payload
        
        print(f'Setting client {address}\'s name to {client_name}...\n>')
        
        self.lock.acquire()
        self.client_name_lists[client_name] = address
        self.lock.release()
        
    def handle_client_connection(self, client_socket: socket.socket, address):
        while True:
            try:
                request = client_socket.recv(1024).decode()
                
                if(request == ''):
                    raise AttributeError
                
                method, payload = parse_client_request(request, address)
                
                # Call method with parsed payload
                if(hasattr(self, method) and callable(getattr(self, method))):
                    getattr(self, method)(payload)

            except ConnectionError:
                print(f"Client {address} disconnected.\n>")
                break
            except Exception as e:
                tests = 3
                shoud_break = False
                
                if not self.client_socket_exists(address):
                    shoud_break = True

                while tests and not shoud_break:
                    ping_sucessful = self.test_connection(client_socket, address)
                    
                    if not ping_sucessful:
                        self.remove_client(address)
                        client_socket.close()
                        
                        print(f"Client {address} disconnected.\n>")
                        shoud_break = True
                        
                    time.sleep(0.5)
                    tests -= 1
                    
                if(shoud_break):
                    print(e)
                    break
    
    def client_name_exists(self, client_name):
        if self.client_name_lists.keys().__contains__(client_name):
            return True
        
    def client_socket_exists(self, address):
        if self.client_socket_lists.keys().__contains__(address):
            return True
          
    def remove_client(self, address):
        if not self.client_socket_exists(address):
            return
        
        self.lock.acquire()
        
        del self.client_socket_lists[address]
        self.remove_client_name(address)
        
        self.lock.release()
        
    def remove_client_name(self, address):
        for client_name, client_address in self.client_name_lists.items():
            if client_address != address:
                continue
            
            if self.client_name_exists(client_name):
                del self.client_name_lists[client_name]
                break
    
    def test_connection(self, client_socket: socket.socket, address):
        ping_sucessful = True
        
        client_is_removed = not client_socket or not self.client_socket_lists.keys().__contains__(address)
        
        if(client_is_removed):
            return False
        
        try:
            client_socket.sendall('Test connection'.encode())
        except ConnectionError:
            ping_sucessful = False

        return ping_sucessful
    
    def ping_client(self, client_name):
        client_address = self.client_name_lists[client_name]
                
        try:
            client = self.client_socket_lists[client_address]
            client.sendall('Server has pinged you !'.encode())
        except ConnectionError as e:
            print(f'Client {client_name} is not available.\n>')
            
    def shutdown(self, payload=None):
        print('\nShutting Down...')
        
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def add_file_reference(self, payload):
        self.lock.acquire()
        
        file_name, file_path, client_address, = payload
        
        if not self.file_references.keys().__contains__(file_name):
            self.file_references[file_name] = []
            
        self.file_references[file_name].append((client_address, file_path))
        
        self.lock.release()
        
    def discover_client (self, hostname):
        files_information = []
        
        client_address = self.client_name_lists[hostname]
        
        for file_name, file_references in self.file_references.items():
            # Check for all file references whose address is the same as client_address
            for client_address, file_path in file_references:
                # Check host and port
                if client_address == client_address:
                    files_information.append({
                        'file_name': file_name,
                        'file_path': file_path
                    })
                    break
                
        print(f'Files from host {hostname}:')
        
        for file_information in files_information:
            print(f'File name: {file_information["file_name"]}, file path: {file_information["file_path"]}')
    
    
        
if __name__ == '__main__':
    server = Server()

    server.start()
