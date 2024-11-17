import csv
import json
import socket

from sseclient import SSEClient as EventSource
from tqdm import tqdm

import pandas as pd

from configs import *


# Function to stream data to a socket
def stream_to_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SOCKET_HOST, SOCKET_PORT))
    server_socket.listen(1)
    print(f"Server started at {SOCKET_HOST}:{SOCKET_PORT}, waiting for client...")
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} established.")

    try:
        for event in EventSource(STREAM_URL):
            try:
                change = json.loads(event.data)
                # Filter events based on 'enwiki' and 'edit' type
                if change.get("wiki") == WIKI and change.get('type') == 'edit':
                    event_data = {
                        "id": change.get("id"),
                        "title": change.get("title"),
                        "timestamp": change.get("timestamp"),
                        "user": change.get("user"),
                        "bot": change.get("bot"),
                        "minor": change.get("minor"),
                        "change": change.get("length", {}).get("new", 0) - change.get("length", {}).get("old", 0),
                        "comment": change.get("comment"),
                    }
                    # Send serialized JSON over the socket
                    client_socket.send((json.dumps(event_data) + "\n").encode('utf-8'))
                    print(event_data)

            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        server_socket.close()


# Run the script in two threads
if __name__ == "__main__":
    # Start the socket server in a separate thread
    stream_to_socket()