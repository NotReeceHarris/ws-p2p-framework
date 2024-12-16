import tkinter
import tkinter.messagebox
from PIL import ImageTk
import customtkinter

import time
import datetime
import threading
import sys
import os

from websockets.sync.server import serve
from websockets.sync.client import connect

from send_recv import send, recv, connected, disconnected

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

""" 
Send on client to server
Receive on server from client
"""

app = None
target = None
port = None
Font_mono = ("Courier New", 13, "normal") 
colours = {
    "you": "#85bd84",
    "friend": "#7c87d6",
    "alert": "#bf6767"
}

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        """ 
        Initialise variables for chat history, client and server connections, and line count
        """
        self.history = []
        self.client = None
        self.server = None
        self.lines = 0

        """
        Set tkinter window properties
        """
        self.icon_path = ImageTk.PhotoImage(file=os.path.join("assets","logo.png"))
        self.wm_iconbitmap()
        self.iconphoto(False, self.icon_path)
        self.title("Disconnected")
        self.geometry(f"{1100}x{580}")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        """ 
        Create textbox used for chat history, register colours for different message types 
        """
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=0, columnspan=4, rowspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.textbox.configure(state="disabled", font=Font_mono)
        self.textbox.tag_config('colour_you', foreground=colours["you"])
        self.textbox.tag_config('colour_friend', foreground=colours["friend"])
        self.textbox.tag_config('colour_alert', foreground=colours["alert"])

        """ 
        Create input field and register enter event to send message
        """
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Message")
        self.entry.configure(state="disabled")
        self.entry.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.entry.bind('<Return>', lambda event: self.send_message())

        """ 
        Create send button and register click event to send message
        """
        self.send_button = customtkinter.CTkButton(master=self, text="Send", command=self.send_message, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.send_button.configure(state="disabled")
        self.send_button.grid(row=3, column=3, padx=10, pady=10, sticky="nsew")

    def recv_message(self, message, sender="Friend"):
        """
        Receive and process a new message, adding it to the chat history.

        Args:
            message (str): The content of the message to be received. If False, the function will return early.
            sender (str, optional): The name of the sender. Defaults to "Friend".

        Returns:
            None

        Effects:
            - Adds the message to the chat history with a timestamp.
            - Calls `update_chat()` to refresh the chat interface or data.
        """

        if message == False:
            return

        self.history.append({
            "sender": sender,
            "message": message,
            "time": datetime.datetime.now()
        })

        self.update_chat()

    def update_chat(self):
        """
        Update the chat display with the latest messages from the history.

        This method:
            - Enables the textbox for editing.
            - Calculates how many new messages need to be added since the last update.
            - Formats and inserts these messages into the textbox with different styles based on the sender:
                - 'You': Messages from the user are colored using 'colour_you'.
                - 'Friend': Messages from friends are colored using 'colour_friend'.
                - 'Alert': Alerts are colored using 'colour_alert'.
                - 'Divider': Displays a special divider with a centered message.
                - Other senders are displayed in default text coloring.
            - Increments the line count for the next update.
            - Disables the textbox after insertion to prevent editing.
            - Scrolls to the end of the textbox to show the latest message.

        No parameters are required as it operates on instance variables.
        """

        self.textbox.configure(state="normal")

        history_length = len(self.history)
        new = (history_length - self.lines)
        to_add = self.history[-new:]

        for i, message in enumerate(to_add, start=1):

            time = message['time'].strftime("%d/%m/%Y %H:%M:%S")

            if message['sender'] == "You":
                self.textbox.insert(tkinter.END, f"[{time}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_you")
            elif message['sender'] == "Friend":
                self.textbox.insert(tkinter.END, f"[{time}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_friend")
            elif message['sender'] == "Alert":
                self.textbox.insert(tkinter.END, f"[{time}] {message['sender'].ljust(6)} : {message['message']}\n", "colour_alert")
            elif message['sender'] == "Divider":
                self.textbox.insert(tkinter.END, f"{'-'*60}\n")
                self.textbox.insert(tkinter.END, f"{message['message']}\n")
                self.textbox.insert(tkinter.END, f"{'-'*60}\n")
            else:
                self.textbox.insert(tkinter.END, f"{message['message']}\n")

        self.lines += 1
        self.textbox.configure(state="disabled")
        self.textbox.see(tkinter.END)

    def is_connected(self):
        """
        Check and update the connection status of the client and server.

        This method:
        - Checks if both the client and server are connected (state == 1).
        - Updates the window title to reflect the connection status.
        - Enables or disables the message entry field and send button based on connection.
        - Sends a special message to the chat indicating connectivity status if connected.

        No parameters are explicitly passed; it uses instance variables:
        - `self.client`: The client object with a `state` attribute.
        - `self.server`: The server object with a `state` attribute.
        - `self.title`: Method to change the window title.
        - `self.entry`: The entry widget for message input.
        - `self.send_button`: The button for sending messages.
        - `self.recv_message`: Method to add messages to the chat history.

        Returns:
            None
        """

        if (self.client is not None and self.client.state == 1 and self.server is not None and self.server.state == 1):
            self.title("Connected")
            self.entry.configure(state="normal")
            self.send_button.configure(state="normal")
            self.recv_message("Two-way communication established", sender="Divider")
            connected(self.client)
        else:
            self.title("Disconnected")
            self.entry.configure(state="disabled")
            self.send_button.configure(state="disabled")
            disconnected()

    def send_message(self):
        """
        Handle the process of sending a message through the client.

        This method:
        - Retrieves the message from the entry widget and strips whitespace.
        - Checks if the message is not empty before proceeding.
        - Attempts to send the message via the client:
            - Parses the message for sending.
            - Sends the parsed message through the client.
            - Adds the sent message to the chat history as from 'You'.
            - Clears the entry field after successful send.
        - Catches and reports any exceptions during the send process.
        - Alerts if the client is not initialized or connected.

        No parameters are explicitly passed; it uses instance variables:
        - `self.entry`: The widget where the user types the message.
        - `self.client`: The client object for sending messages.
        - `self.recv_message`: Method to add messages to the chat history.

        Returns:
            None
        """

        message = self.entry.get().strip()

        if message == "":
            return

        if self.client:   # Check if client is initialized
            try:
                parsedMessage = send(message)
                self.client.send(parsedMessage)
                self.recv_message(message, sender="You")
                self.entry.delete(0, tkinter.END)

            except Exception as e:
                self.recv_message(f"Failed to send message: {str(e)}", sender="Alert")
        else:
            self.recv_message("Client not connected", sender="Alert")

def handler(websocket):
    app.recv_message("Client connected", sender="Alert")
    app.server = websocket
    app.is_connected()
    while websocket.state:
        try:
            # Wait for incoming messages
            message = websocket.recv()
            decoded_message = recv(message)  # Assuming recv is your custom function to decode messages
            app.recv_message(decoded_message, sender="Friend")
        except Exception as e:
            break
    app.is_connected()

def run_server():
    with serve(handler, "localhost", port, max_size=10 * 1024 * 1024) as server:
        app.recv_message(f"Server started listening on port {port}", sender="Alert")
        server.serve_forever()

def run_client():
    print(f"ws://{target}")
    app.recv_message(f"Connecting to {target}", sender="Alert")
    
    while True:
        try:
            with connect(f"ws://{target}") as client:
                app.recv_message(f"Connected to {target}", sender="Alert")
                app.client = client
                app.is_connected()
                
                # Keep the connection open
                while client.state:
                    try:
                        message = client.recv()
                        try:
                            decoded_message = recv(message)
                            app.recv_message(decoded_message, sender="Friend")
                        except Exception as e:
                            app.recv_message(f"Failed to decode message: {str(e)}", sender="Alert")
                    except Exception as e:
                        app.recv_message(f"Client disconnected: {str(e)}", sender="Alert")
                        break
        except Exception as e:
            app.is_connected()
            app.recv_message(f"Failed to connect to server on port {port}: {str(e)}", sender="Alert")
            # Wait before retrying to avoid spamming the server with connection attempts
            time.sleep(5)

def main(arg_target, arg_port):
    global app
    app = App()

    global target
    target = arg_target

    global port
    port = int(arg_port)
    
    # Start the WebSocket server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # This thread will be killed when the main program exits
    server_thread.start()

    # Start the WebSocket client in a separate thread
    client_thread = threading.Thread(target=run_client)
    client_thread.daemon = True
    client_thread.start()
    
    # Start the Tkinter main loop
    app.mainloop()

if __name__ == "__main__":

    arg_target = None
    arg_port = None

    # If you want to handle each argument individually:
    for i, arg in enumerate(sys.argv[1:], 1):
        if (arg == '--target'):
            arg_target = sys.argv[1:][i]
        elif (arg == '--port'):
            arg_port = sys.argv[1:][i]

    if not arg_port or not arg_target:
        print('Usage: python main.py --target <address> --port <port>')
    else:
        main(arg_target, arg_port)