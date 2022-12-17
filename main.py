import sys
from application.app import App
from sockets.server import ServerSocket


if __name__ == "__main__":

    args = sys.argv
   
    if (args[1] == 'runserver'):
        server = ServerSocket()
        if server.setup():
            server.run()

    if (args[1] == 'app'):
        username = input('> Username: ')
        room = input('> Room: ')
        app = App({'username': username, 'room': room})
