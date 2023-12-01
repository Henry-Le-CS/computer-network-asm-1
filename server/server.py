import socket
import threading
import sys 
import os
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

        self.client_lists = {}  # {address: client}
        self.lock = threading.Lock()
    def start(self):
        print('Starting the server on %s:%s' % (self.server_host, self.server_port))

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_host, self.server_port))
        self.server.listen(5)

        while True:
            try:
                client, address = self.server.accept()
                print('Client %s:%s connected.' % (address[0], address[1]))

                self.client_lists[address] = client

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
                
    def handle_client_connection(self, client_socket: socket.socket, address):
        while True:
            try:
                request = client_socket.recv(1024)

                payload = request.decode()
                
                if(payload == ''):
                    raise AttributeError('Empty payload.')

            except ConnectionError:
                print(f"Client {address} disconnected.")
                break
            except Exception as e:
                ping_sucessful = self.ping_client(client_socket, address)
                
                if( not ping_sucessful ):
                    self.remove_client(address)
                    client_socket.close()
                    
                    print(f"Client {address} disconnected.")
                break

    def remove_client(self, address):
        self.lock.acquire()
        del self.client_lists[address]
        self.lock.release()
        
    def ping_client(self, client_socket: socket.socket, address):
        ping_sucessful = True
        
        try:
            client_socket.sendall('PING'.encode())
        except ConnectionError as e:
            ping_sucessful = False

        return ping_sucessful
    
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
