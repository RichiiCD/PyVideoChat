import tkinter as tk
import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
import cv2
import time



class Inset:

    def __init__(self, root, row, column, width, height):
        # Create and position a frame with specified width and height
        self.frame = ctk.CTkFrame(master=root, width=width, height=height)
        self.frame.grid(row=row, column=column, padx=10, pady=10)
        #tk_frame.pack_propagate(False)

        # Create a label widget and place it in the frame
        self.label = tk.Label(self.frame)
        self.label.pack()


class GUI:

    def __init__(self, handle_close):
        self.state = 'open'

        self.insets = []
        self.insets_num = 1
        self.insets_per_row = 4
        self.insets_rate = 0.1

        self.users = []

        self.current_frame = None

        self.root = ctk.CTk()

        self.root.protocol("WM_DELETE_WINDOW", handle_close)

    # Displays the insets on the main window.
    def display(self): 
        # Initialize column and row indices
        column = 0
        row = 0

        for _ in range(0, self.insets_num):
            # Create new inset with specified dimensions and position
            inset = Inset(self.root, row=row, column=column, width=430, height=350)
            self.insets.append(inset)

            column += 1

            # If the column index reaches the number of insets per row, reset the column index and increment the row index
            if column == self.insets_per_row:
                column = 0
                row += 1
        
        # Start the infinite loop that updates the main window
        self.root_update_loop()

    # Processes a video frame and converts it into an image that can be displayed on the GUI
    def process_frame(self, frame):
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        # Convert the frame from BGR to RGBA color space
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        # Create and convert the PIL image to a PhotoImage object
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        return imgtk

    # Displays a processed video frame in one of the insets
    def display_frame(self, frame):
        if frame:
            # Process the frame
            processed_frame = self.process_frame(frame['frame'])
            # Get the username associated with the frame
            frame_username = frame['username']

            if frame_username not in self.users:
                # Add the username to the list of users if is not in the list
                self.users.append(frame_username)

            # Get the index of the inset that corresponds to the username
            inset_index = self.users.index(frame_username)
            
            # Update the image displayed in the inset
            self.insets[inset_index].label.imgtk = processed_frame
            self.insets[inset_index].label.configure(image=processed_frame)

    # Infinite loop that continuously updates the main GUI window and displays changes in the video
    def root_update_loop(self):
        while self.state == 'open':
            time.sleep(self.insets_rate)
            self.display_frame(self.current_frame)
            self.root.update()

    # Close the GUI
    def close_windows(self):
        self.state = 'close'
        self.root.destroy()