import socket
import sys
from enum import Enum

HOST = sys.argv[1]  
PORT = sys.argv[2]  

class RequestType(Enum):
    CONNECTION_TEST = 'CONNECTION_TEST'

class ResponeType(Enum):
    OK = 'OK'
    INVALID_REQUEST = "INVALID_REQUEST"

print(f"server={(HOST, PORT)} is up now.")

def connect_to_load_balancer(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, int(port)))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break
                    elif data == RequestType.CONNECTION_TEST.value:
                        print("Received connection check from client")
                        conn.sendall(ResponeType.OK.value.encode())
                    else:
                        try:
                            item = int(data)
                            print(f"It's instance number {item}")
                            conn.sendall(ResponeType.OK.value.encode())
                        except ValueError:
                            conn.sendall(ResponeType.INVALID_REQUEST.value.encode())
                            print("Invalid data received from client:", data)

connect_to_load_balancer(HOST, PORT)

print(f"server={(HOST, PORT)} is down now.")