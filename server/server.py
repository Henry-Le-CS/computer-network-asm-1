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
        """
        client_name_lists = {
            client_name: {
                'host': host,
                'port': port,
                'upload_port': upload_port
            }
        }
        """
        self.client_name_lists = {}
        
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
        """
            Start the server and listen for incoming connections
        """
        print('Starting the server on %s:%s' % (self.server_host, self.server_port))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_host, self.server_port))
        self.server.listen(5)

        # Start CLI thread
        cli_thread = threading.Thread(target=self.cli)
        cli_thread.start()
        
        while True:
            try:
                client, address = self.server.accept()
                print('Client %s:%s connected.' % (address[0], address[1]))
                
                self.client_socket_lists[address] = client

                # Create thread to handle each client connection
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
        """
            Listen for user input and execute commands
        """
        while True:
            try:
                command = input('> ')
                
                if command == '':
                    continue
                
                method, payload = parse_server_cmd(command)
                
                # Call method with parsed payload
                if(hasattr(self, method) and callable(getattr(self, method))):
                    # The method is the Server's function, payload is the argument
                    getattr(self, method)(payload)
                
                
            except Exception as e:
                print(e)
            except BaseException:
                self.shutdown()
                    
    def handle_client_connection(self, client_socket: socket.socket, address):
        """
            Handle client connection by parsing their requests and execute the corresponding method

        Args:
            client_socket (socket.socket): The client's socket
            address (tuple(str, int)):  The client's address

        Raises:
            AttributeError: If the client is disconnected
        """
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
                self.remove_client(address)
                print(f"Client {address} disconnected.\n> ", end='')
                print('> ')
                break
            except Exception:
                tests = 3
                shoud_break = False
                
                if not self.is_client_socket_exists(address):
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
            client_socket.sendall(f'Server at {self.server_host}:{self.server_port} is testing your connection'.encode())
        except ConnectionError:
            ping_sucessful = False

        return ping_sucessful

    def ping_client(self, client_name):
        if not self.is_client_name_exists(client_name):
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
        """
            Set client addresses on client's request
        Args:
            payload (tuple): client_name, address, client_upload_port
        """
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

    def is_client_name_exists(self, client_name):
        if self.client_name_lists.keys().__contains__(client_name):
            return True
        
    def is_client_socket_exists(self, address):
        if self.client_socket_lists.keys().__contains__(address):
            return True

    def publish_filename(self, payload):
        """
            Add file name and corresponding uploader, file path to file_references
        Args:
            payload (_type_): file_name, file_path, uploader_address
        """
        self.lock.acquire()
        
        file_name, file_path, uploader_address = payload
        print('[Server] publishing', file_name, file_path)
        
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

    def init_publish(self, payload):
        files, file_path, uploader_address = payload
        splitted_files = files.split(':')

        # Debugging
        i = 0
        for file in splitted_files:
            print('- ', i, file)
            i += 1

        for file in splitted_files:
            self.publish_filename((file, file_path, uploader_address))

        print('[Server] pre-publishing with', files, file_path, uploader_address)
        
    def remove_local_file(self, payload):
        # return
        self.lock.acquire()
        file_name, file_path, uploader_address = payload

        if not self.file_references.keys().__contains__(file_name):
            print('Print not even existed, returning')
            return

        for client_address, fpath in self.file_references[file_name]:
            if file_path == fpath and client_address == uploader_address:
                print('found match, removing')
                self.file_references[file_name].remove((uploader_address, fpath))
                return
        
        self.lock.release()
        
    def discover_client (self, hostname):
        files_information = []
        
        if not self.is_client_name_exists(hostname):
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
            
    def fetch_peers (self, payload):        
        file_name, address = payload
        
        client = self.client_socket_lists[address]
        
        if(not self.file_references.keys().__contains__(file_name)):
            client.sendall(f'No peer has file {file_name}.'.encode())
            return
        
        res = ['PEERS'] # keyword
        res.append(file_name)
        
        for uploader_address, file_path in self.file_references[file_name]:
            is_client_fetching_itself = self.isCurrentClient(
                                            address=address, 
                                            uploader_address=uploader_address
                                        )
            
            if is_client_fetching_itself:
                continue
            
            client_name = self.get_client_name(uploader_address)
            res.append(f'{client_name} {uploader_address[0]} {uploader_address[1]} {file_path}')       
        
        message = '\n'.join(res)
        
        client.sendall(message.encode())

    def get_peers(self, payload):
        # This methods used mostly for UI
        file_name, address = payload

        print('[Server] Sending peers for ...')

        client = self.client_socket_lists[address]
        
        if(not self.file_references.keys().__contains__(file_name)):
            client.sendall(f'No peer has file {file_name}.'.encode())
            return
        
        res = ['SET_PEERS'] # keyword
        res.append(file_name)
        
        for uploader_address, file_path in self.file_references[file_name]:
            is_client_fetching_itself = self.isCurrentClient(
                                            address=address, 
                                            uploader_address=uploader_address
                                        )
            
            if is_client_fetching_itself:
                continue
            
            client_name = self.get_client_name(uploader_address)
            res.append(f'{client_name} {uploader_address[0]} {uploader_address[1]} {file_path}')       
        
        message = '\n'.join(res)
        
        client.sendall(message.encode())

    def isCurrentClient(self, address, uploader_address):        
        """
            Check if the current client is fetching or executing the command itself
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
    
    def remove_client(self, address):        
        self.lock.acquire()
        
        self.remove_file_reference(address)
        self.remove_client_name(address)
        self.remove_client_socket(address)
        
        self.lock.release()
    
    def remove_client_socket(self, address):
        if not self.is_client_socket_exists(address):
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

    def fetch_available_peers(self, payload):
        client_address = payload
        client_soc = self.client_socket_lists[client_address]
        
        peers = []
        index = 1
        # hostname, host, port, upload_port
        for client_name, client_addresses in self.client_name_lists.items():
            uploader_address = (client_addresses['host'], str(client_addresses['upload_port']))
            
            is_client_fetching_itself = self.isCurrentClient(
                                            address=client_address, 
                                            uploader_address=uploader_address
                                        )
            
            if is_client_fetching_itself:
                continue
            
            peers.append(f'\n{index}) Hostname: {client_name}, IP: {client_addresses["host"]}, Port: {client_addresses["port"]}, Upload port: {client_addresses["upload_port"]}\n')
            index += 1
        
        if len(peers) == 0:
            client_soc.sendall('No fetchable peer is available.'.encode())
            return
        
        message = '\n'.join(peers)
        client_soc.sendall(message.encode())
    
    def fetch_all_available_files(self, payload):
        client_address = payload
        client_soc = self.client_socket_lists[client_address]
        
        files = []
        index = 1
        
        for file_name, file_references in self.file_references.items():
            for uploader_address, file_path in file_references:
                
                is_client_fetching_itself = self.isCurrentClient(
                                                address=client_address, 
                                                uploader_address=uploader_address
                                            )
                
                if is_client_fetching_itself:
                    continue
                
                client_name = self.get_client_name(uploader_address)
                files.append(f'{index}) File name: {file_name}, File path: {file_path}, Host: {client_name}, IP: {uploader_address[0]}, Upload port: {uploader_address[1]}')
                index += 1
        
        if len(files) == 0:
            client_soc.sendall('No fetchable file is available on other peer.'.encode())
            return
        
        message = '\n'.join(files)
        client_soc.sendall(message.encode())

    def get_all_available_peers(self, payload):
        print('[SERVER] getting avail peers')
        client_address = payload
        client_soc = self.client_socket_lists[client_address]

        res = []
        index = 1
        # hostname, host, port, upload_port
        for client_name, client_addresses in self.client_name_lists.items():
            uploader_address = (client_addresses['host'], str(client_addresses['upload_port']))
            
            is_client_fetching_itself = self.isCurrentClient(
                                            address=client_address, 
                                            uploader_address=uploader_address
                                        )
            
            if is_client_fetching_itself:
                continue
            
            res.append(f'\n{index}) Hostname: {client_name}, IP: {client_addresses["host"]}, Port: {client_addresses["port"]}, Upload port: {client_addresses["upload_port"]}\n')
            index += 1
        
        if len(res) == 0:
            client_soc.sendall('No fetchable peer is available.'.encode())
            return
        
        message = '\n'.join(res)
        client_soc.sendall(message.encode())

    def get_all_available_files(self, payload):
        print('listing files')
        client_address = payload
        client_soc = self.client_socket_lists[client_address]
        
        files = ['SET_AVAILABLE_FILES']
        index = 1
        
        for file_name, file_references in self.file_references.items():
            print('loop through', file_name, file_references)
            is_fetching_itself_flag = False
            for uploader_address, file_path in file_references:
                
                if self.isCurrentClient(address=client_address, uploader_address=uploader_address):
                    is_fetching_itself_flag = True
                    break
            
            if not is_fetching_itself_flag:
                client_name = self.get_client_name(uploader_address)
                files.append(f'{file_name}')
                index += 1
        
        if len(files) == 0:
            client_soc.sendall('No fetchable file is available on other peer.'.encode())
            return
        
        message = '\n'.join(files)
        client_soc.sendall(message.encode())

        
if __name__ == '__main__':
    server = Server(server_host='192.168.1.11')

    server.start()
