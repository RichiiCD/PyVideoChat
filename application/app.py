import sys
import numpy
import cv2 as cv
import threading
from application.camera import Camera
from application.gui import GUI
from sockets.client import ClientSocket


class App:

    # Initializes the App class, setting up the client socket, camera, and GUI
    def __init__(self, client_data):
        # Initialize the client socket with the given client data and set the on_message callback to receive_frame
        self.client = ClientSocket(client_data=client_data,
                                   on_message=self.receive_frame)

        # If the client socket is successfully set up, start it and set up the camera and GUI
        if self.client.setup():
            self.client.start()

            self.camera = Camera(handle_frame=self.handle_frame)
            self.camera_thread = threading.Thread(target=self.camera.capture)
            self.camera_thread.start()

            self.gui = GUI(handle_close=self.close_app)
            self.gui.display()

    # Sends the given frame to the client socket
    def handle_frame(self, frame):
        self.client.send(frame)

    # Receives a frame from the client socket and decodes it, updating the GUI with the decoded frame
    def receive_frame(self, frame):
        new_frame = frame['message']
        array_frame = numpy.frombuffer(new_frame, dtype='uint8')
        decoded_frame = cv.imdecode(array_frame, 1)

        self.gui.current_frame = ({'username': frame['username'], 'frame': decoded_frame})

    # Close the app
    def close_app(self):
        self.client.close_connection()
        self.camera.close_camera()
        self.gui.close_windows()
        sys.exit()