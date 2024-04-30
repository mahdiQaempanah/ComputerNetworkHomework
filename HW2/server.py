import socket
import sys

HOST = sys.argv[1]  
PORT = sys.argv[2]  

print(f"server={(HOST, PORT)} is up now.")

def connect_to_load_balancer(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        break
                    elif data == "connection_check":
                        print("Received connection check from client")
                        conn.sendall(b"Server is alive")
                    else:
                        try:
                            item = int(data)
                            print(f"It's instance number {item}")
                            conn.sendall(b"OK")
                        except ValueError:
                            print("Invalid data received from client:", data)

connect_to_load_balancer(HOST, PORT)

print(f"server={(HOST, PORT)} is down now.")