import socket
import threading
import sys 
import os

from server.server_helper import switch_server_cmd, switch_client_request

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
                
                if client and address:
                    self.client_socket_lists[address] = client
                    self.set_client_name('client1', client)

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
                command = input('>')

                method, payload = switch_server_cmd(command)
                print(method, payload)
                if(hasattr(self, method) and callable(getattr(self, method))):
                    getattr(self, method)(payload)
                
                
            except Exception as e:
                print(e)
            except BaseException:
                self.shutdown()
    
    def set_client_name (self, client_name, client):
        print(f'Setting client name to {client_name}...')
        self.lock.acquire()
        self.client_name_lists[client_name] = client
        self.lock.release()
        
    def handle_client_connection(self, client_socket: socket.socket, address):
        while True:
            try:
                request = client_socket.recv(1024).decode()
                
                if(request == ''):
                    raise AttributeError('Empty request.')
                
                method, payload = switch_client_request(request, address)
                
                if(hasattr(self, method) and callable(getattr(self, method))):
                    getattr(self, method)(payload)

            except ConnectionError:
                print(f"Client {address} disconnected.")
                break
            except Exception as e:
                ping_sucessful = self.test_connection(client_socket, address)
                
                if( not ping_sucessful ):
                    self.remove_client(address)
                    client_socket.close()
                    
                    print(f"Client {address} disconnected.")
                break

    def remove_client(self, address):
        self.lock.acquire()
        del self.client_socket_lists[address]
        self.lock.release()
    
    def test_connection(self, client_socket: socket.socket, address):
        ping_sucessful = True
        
        try:
            client_socket.sendall('PING'.encode())
        except ConnectionError:
            ping_sucessful = False

        return ping_sucessful
    
    def ping_client(self, client_name):
        client_socket = self.client_name_lists[client_name]
        print(f'Pinging {client_name}...')
        
        try:
            client_socket.sendall('PINGS'.encode())
        except ConnectionError as e:
            print(f'Client {client_name} is not available.')
            
    def shutdown(self):
        print('\nShutting Down...')
        self.server.close()
        
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    server = Server()

    server.start()
