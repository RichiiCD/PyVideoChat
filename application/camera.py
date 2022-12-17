import sys
import numpy
import cv2 as cv


class Camera:
    """Class to handle camera operations"""

    def __init__(self, handle_frame):
        """Initialize camera and set encoding parameters

        Args:
        handle_frame: function to handle frames captured by the camera
        """
        self.cap = cv.VideoCapture(0)

        # Exit if camera cannot be opened
        if not self.cap.isOpened():
            print("Cannot open camera")
            sys.exit()
        
        # Set encoding parameters for JPEG with quality 90%
        self.encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 90]

        self.handle_frame = handle_frame

    # Capture frames from the camera and handle them using the handle_frame function
    def capture(self):
        while True:
            # Read frame from camera
            ret, frame = self.cap.read()

            if not ret:
                break
            
            # Encode frame as JPEG and convert it to bytes
            _, encoded_frame = cv.imencode('.jpg', frame, self.encode_param)
            data = numpy.array(encoded_frame)
            bytes_data = data.tobytes()

            # Handle frame with handle_frame function
            self.handle_frame(bytes_data)

    # Close camera and release resources
    def close_camera(self):
        self.cap.release()
        