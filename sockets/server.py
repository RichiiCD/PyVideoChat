import socket
import threading
import pickle
import os
import ssl
from sockets.custom_socket import CustomSocket
from sockets.log import Log


class ServerSocket(CustomSocket):
    ''' Chat application server socket class'''

    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        # Initialize the parent socket by passing the required arguments
        super().__init__(64, ('localhost', 5000), 'utf-8')

        # Client and connections list containing the active clients sockets connections and their information 
        self.client_list = {}
        self.connection_list = []
        self.status = 'open'

        # Define the TLS security context
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain("./sockets/ssl/certificate.crt", "./sockets/ssl/private.key")

        # Wrap (TLS) the server socket
        self.wconn = self.context.wrap_socket(self.conn, server_side=True)

    # Configures the initial options. Called before the server starts
    def setup(self):
        Log('OKGREEN', 'STARTING', 'Server is starting')

        # Allow connections from clients with the same address
        self.wconn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to bind on configured server address
        try:
            self.wconn.bind(self.server)
            return True

        except OSError:
            Log('FAIL', 'SERVER ERROR', f'Unable to bind on server {self.server[0]}:{self.server[1]}')
            return False
    
    # Handle connection closed
    def close_connection(self, conn, addr):
        Log('OKBLUE', 'CONNECTION CLOSED', f'{addr[0]} closed the connection')
        self.connection_list.remove(conn)
        del self.client_list[conn]
        conn.close()

    # Handle a received client's message
    def receive_message(self, conn):
        try:
            message_header = conn.recv(self.header)

            if not len(message_header):
                return False
            
            message_length = int(message_header.decode('utf-8'))

            buffer = b''
            count = message_length

            while count:
                new_buffer = conn.recv(count)
                if not new_buffer:
                    return False
                buffer += new_buffer
                count -= len(new_buffer)

            return {'header': message_header.decode('utf-8'), 'data': buffer}
        
        except:
            return False

    # Send the client's message to all the clients in the same room
    def send_broadcast_message(self, msg, sender_conn):
        sender_user = self.client_list[sender_conn]
        #decoded_msg = pickle.loads(msg)
        #decoded_msg = msg.decode('utf-8')
        #decoded_msg = numpy.frombuffer(msg)

        for client, user in self.client_list.items():
            if sender_user['room'] == user['room']:
                #pickle_data = pickle.dumps({'username': sender_user['username'], 'message': decoded_msg})
                pickle_data = pickle.dumps({'username': sender_user['username'], 'message': msg})
                msg_header = f"{len(pickle_data):<{self.header}}".encode('utf-8')
                client.send(msg_header + pickle_data)

    # Handle client socket connection
    def client_handler(self, conn, addr):
        ''' Every client connections runs into different thread '''

        connected = True

        while connected:
            msg = self.receive_message(conn)

            # If no message received from client, the connection is closed and the client is removed from the list
            if msg is False:
                connected = False
                self.close_connection(conn, addr)
                continue
            
            self.send_broadcast_message(msg['data'], conn)
    
    def connection_hanlder(self, conn, addr):
        # Receive the client configuration data
        client_data = self.receive_message(conn)
        client_data = pickle.loads(client_data['data'])
            
        # Save the user configuration and information data
        self.connection_list.append(conn)
        self.client_list[conn] = client_data

        self.client_handler(conn, addr)

    # Called after the server setup. Event loop to accept and handle new clients connections.
    def run(self):

        # Server socket starts listening for new connections from client sockets 
        self.wconn.listen()
        Log('OKGREEN', 'LISTENING', f'Server is listening on {self.server}')

        while True:
            # Wait to receive a new connection
            conn, addr = self.wconn.accept()

            Log('OKBLUE', 'NEW CONNECTION', f'{addr} connected')
            
            # Create a thread to handle client socket connection
            thread = threading.Thread(target=self.connection_hanlder, args=(conn, addr))
            thread.start()



