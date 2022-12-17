import sys
import os
import errno
import threading
import pickle
import socket
import ssl
from sockets.custom_socket import CustomSocket
from sockets.log import Log


class ClientSocket(CustomSocket):
    ''' Chat application client socket class'''

    def __init__(self, client_data, on_message):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Initialize the parent socket by passing the required arguments
        super().__init__(64, ('localhost', 5000), 'utf-8')

        # Client and user variables
        self.status = 'close'
        self.username = client_data['username']
        self.room = client_data['room']
        self.on_message = on_message

        # Define the TLS security context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.load_verify_locations("./sockets/ssl/certificate.crt")

        # Wrap (TLS) the server socket
        self.wconn = self.context.wrap_socket(self.conn, server_hostname="localhost")
    
    # Called before the client socket connection starts. Configures the initial options
    def setup(self):
        Log('OKCYAN', 'CONNECTING', 'Connecting to remote server...')
        remote_server = f"{self.server[0]}:{self.server[1]}"

        # Try to connect to remote server
        try:
            self.wconn.connect(self.server)
            self.status = 'open'
            Log('OKGREEN', 'CONNECTING', f'Connection established with remote server ({remote_server})')
            return True

        except ConnectionRefusedError:
            Log('FAIL', 'CONNECTION ERROR', f'Connection refused by remote server')
            
        except TimeoutError:
            Log('FAIL', 'CONNECTION ERROR', f'Unable to connect to remote server ({remote_server})')
        
        except socket.gaierror:
            Log('FAIL', 'CONNECTION ERROR', f'Error on remote server ({remote_server}) configuration')
        
        return False

    # Called after the client setup. Configures communication with the remote server
    def start(self):
        if (self.status == 'open'):
            self.wconn.setblocking(True)
            
            # Send the client configuration 
            client_data = {'username': self.username, 'room': self.room}
            client_data = pickle.dumps(client_data)
            self.send(client_data)

            # Create a thread for handle receiving messages
            t = threading.Thread(target=self.receive)
            t.start()

    # Function to handle receiving messages from the remote server
    def receive(self):
        while self.status == 'open':
            try:
                msg_header = self.wconn.recv(self.header)

                # If the received header message has no length, the connection is closed
                if not len(msg_header):
                    Log('FAIL', 'CLOSED CONNECTION', 'Connection closed by the remote server')
                    sys.exit()

                # Receive the rest of the message
                msg_length = int(msg_header.decode('utf-8'))
                
                buffer = b''
                count = msg_length

                while count:
                    new_buffer = self.wconn.recv(count)
                    if not new_buffer:
                        return False
                    buffer += new_buffer
                    count -= len(new_buffer)
                
                msg = pickle.loads(buffer)

                self.on_message({'username': msg['username'], 'message': msg['message']})        

            # If no input from socket connection, continue and try again 
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    self.wconn.close()
                    Log('FAIL', 'READING ERROR', 'Connection closed by remote server')
                    sys.exit()
                continue

            """ except Exception as e:
                self.wconn.close() 
                Log('FAIL', 'FATAL ERROR', str(e))
                sys.exit() """
    
    # Send a message to remote server
    def send(self, message):
        if message:
            self.wconn.send(self.format_message(message))
    
    # Close the connection between client and server
    def close_connection(self):
        self.wconn.shutdown(how=socket.SHUT_RDWR)
        Log('OKCYAN', 'CLOSED', 'Connection closed with remote server')

