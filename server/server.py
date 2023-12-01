import socket
import threading
class Server:
    def __init__(
            self, 
            server_host = "",
            server_port = 7734,
            upload_port = None,
        ) -> None:
        
        self.server_host = server_host
        self.server_port = server_port
        self.upload_port = upload_port
    
    def start(self):
        print('Starting the server on %s:%s' % (self.server_host, self.server_port))
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_host, self.server_port))
        self.server.listen(5)
        
        while True:
            try:
                client, address = self.server.accept()
                print('Client %s:%s connected.' % (address[0], address[1]))

                # Create thread to handle client request
                client_handler = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client, address)
                )
                
                client_handler.start()
            except KeyboardInterrupt:
                print('Server is shutting down...')
                self.server.close()
                break;
            
    def handle_client_connection(self, client_socket, address):
        request = client_socket.recv(1024)
        
        print('Received %s' % request)
        
        response = 'P2P-CI/1.0 200 OK\n' + \
                   'Date: Mon, 27 Mar 2000 12:00:00 GMT\n' + \
                   'OS: Mac OS\n' + \
                   'Last-Modified: Wed, 22 Mar 2000 12:00:00 GMT\n' + \
                   'Content-Length: 128\n' + \
                   'Content-Type: text/plain\n' + \
                   'Content-Disposition: attachment; filename="test.txt"\n' + \
                   'Content-Transfer-Encoding: binary\n' + \
                   'Content-MD5: 1234567890\n' + \
                   'X-File-Name: test.txt\n' + \
                   'X-File-Size: 128\n' + \
                   'X-File-Type: text/plain\n' + \
                   'X-File-Hash: 1234567890\n' + \
                   'X-File-Description: This is a test file.\n\n' + \
                   'This is a test file.'
        
        client_socket.send(response.encode())
        client_socket.close()
        
if __name__ == '__main__':
    server = Server()
    
    server.start()