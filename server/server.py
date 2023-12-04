import socket
import threading
import sys 
import os
import time
import copy
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
        self.client_name_lists = {}  # {client_name: (host, port, uploader_port)}
        
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
                print('> ')
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
                print(f"Client {address} disconnected.\n> ", end='')
                print('> ')
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
                        
                        print(f"Client {address} disconnected.\n> ", end='')
                        shoud_break = True
                        
                    time.sleep(0.5)
                    tests -= 1
                    
                if(shoud_break):
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
        if not self.client_name_exists(client_name):
            print(f'Client {client_name} not found.')
            return
        
        client_addresses = self.client_name_lists[client_name]
        try:
            socket_address = (client_addresses['host'], client_addresses['port'])
            
            client = self.client_socket_lists[socket_address]
            client.sendall(f'Server at {self.server_host}:{self.server_port} has pinged you !'.encode())
            
            print(f'Pinged client {client_name} at {socket_address}.\n', end='')
        except ConnectionError as e:
            print(f'Client {client_name} is not available.\n')

    def set_client_addresses(self, payload):
        client_name, address, client_upload_port = payload

        print(f'Setting client {address}\'s name to {client_name}...\n> ', end='')

        host, port = address

        self.lock.acquire()
        
        self.client_name_lists[client_name] = {
            'host': host,
            'port': int(port),
            'upload_port': int(client_upload_port)
        }
        
        self.lock.release()

    def client_name_exists(self, client_name):
        if self.client_name_lists.keys().__contains__(client_name):
            return True
        
    def client_socket_exists(self, address):
        if self.client_socket_lists.keys().__contains__(address):
            return True
          
    def remove_client(self, address):        
        self.lock.acquire()
        
        self.remove_file_reference(address)
        self.remove_client_name(address)
        self.remove_client_socket(address)
        
        self.lock.release()
    
    def remove_client_socket(self, address):
        if not self.client_socket_exists(address):
            return
        
        new_client_socket_lists = {}
        
        for client_address, client_socket in self.client_socket_lists.items():
            if client_address == address:
                continue
            
            new_client_socket_lists[client_address] = client_socket

        self.client_socket_lists = new_client_socket_lists
    
    def remove_client_name(self, address):
        new_client_name_lists = {}
        
        for client_name, client_addresses in self.client_name_lists.items():
            client_address = (client_addresses['host'], str(client_addresses['port']))
            address = (address[0], str(address[1]))
            
            if address == client_address:
                continue
            
            new_client_name_lists[client_name] = client_addresses
            
        self.client_name_lists = new_client_name_lists
    
    def remove_file_reference(self, address):
        new_file_references = {}
        
        for file_name, file_references in self.file_references.items():
            new_file_references[file_name] = []
            
            for uploader_address, file_path in file_references:
                if self.isCurrentClient(address=address, uploader_address=uploader_address):
                    continue
                
                new_file_references[file_name].append((uploader_address, file_path))
                
        self.file_references = new_file_references
        
    def shutdown(self, payload=None):
        print('\nShutting Down...')
        
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def add_file_reference(self, payload):
        self.lock.acquire()
        
        file_name, file_path, uploader_address = payload
        
        # Work around: file_path will be destructured from self.file_references[file_name]. So we need a cloned variable
        path = file_path
        
        if not self.file_references.keys().__contains__(file_name):
            self.file_references[file_name] = []
            
        for client_address, file_path in self.file_references[file_name]:
            if path == file_path and client_address == uploader_address:
                print(f'File {file_name} at {path} directory has already been recorded.\n')
                return
        
        self.file_references[file_name].append((uploader_address, path))
        
        self.lock.release()
        
    def discover_client (self, hostname):
        files_information = []
        
        if not self.client_name_exists(hostname):
            print(f'Client {hostname} not found.')
            return
        
        client_addresses = self.client_name_lists[hostname]
        address = (client_addresses['host'], str(client_addresses['upload_port']))
        
        for file_name, file_references in self.file_references.items():
            # Check for all file references whose address is the same as client_address
            for uploader_address, file_path in file_references:
                # Check host and port
                if uploader_address == address:
                    files_information.append({
                        'file_name': file_name,
                        'file_path': file_path
                    })
                
        print(f'Files from host {hostname}:')
        
        for file_information in files_information:
            print(f'File name: {file_information["file_name"]}, file path: {file_information["file_path"]}')
 
    def get_client_name(self, address):
        for client_name, client_addresses in self.client_name_lists.items():
            uploader_address = (client_addresses['host'], str(client_addresses['upload_port']))
            
            if uploader_address == address:
                return client_name
            
    def isCurrentClient(self, address, uploader_address):        
        """
            The purpose of this function is to find the upload address of the current client who is fetching data
            By checking the client's host and port, we can find the upload address of the client
            
            If the upload address match the input, then the client is fetching / calling itself
        Args:
            address (tuple): (host, port)
            uploader_address (tuple): (host, upload_port)

        Returns:
            boolean: is client fetching itself
        """
        for client_name, client_addresses in self.client_name_lists.items():
            if client_addresses['host'] == address[0] and client_addresses['port'] == address[1]:
                uploader_addr = (client_addresses['host'], str(client_addresses['upload_port']))
            
                if uploader_addr == uploader_address:
                    return True
            
        return False
            
    def fetch_peers (self, payload):        
        file_name, address = payload
        
        client = self.client_socket_lists[address]
        
        if(not self.file_references.keys().__contains__(file_name)):
            client.sendall(f'No peer has file {file_name}.'.encode())
            return
        
        res = ['PEERS'] # keyword
        res.append(file_name)
        
        for uploader_address, file_path in self.file_references[file_name]:
            if self.isCurrentClient(address=address, uploader_address=uploader_address):
                continue
            
            client_name = self.get_client_name(uploader_address)
            res.append(f'{client_name} {uploader_address[0]} {uploader_address[1]} {file_path}')       
        
        message = '\n'.join(res)
        
        client.sendall(message.encode())
        
if __name__ == '__main__':
    server = Server(server_host='192.168.1.203')

    server.start()
