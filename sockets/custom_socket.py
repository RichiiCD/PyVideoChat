import socket
import pickle


class CustomSocket:
    ''' Custom socket parent class for the server/client sockets inherit '''

    def __init__(self, header, server, format):
        self.header = header
        self.server = server
        self.format = format

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def format_message(self, msg):
        msg_header = f"{len(msg):<{self.header}}".encode('utf-8')
        return msg_header + msg
