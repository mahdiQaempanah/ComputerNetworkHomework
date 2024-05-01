import socket
import threading
import os
from queue import Queue
import re 
from enum import Enum
import time 

config_path = './config'
ip = "127.0.0.1"
port = 65430

class RequestType(Enum):
    CONNECTION_TEST = 'CONNECTION_TEST'

class ResponeType(Enum):
    OK = 'OK'
    INVALID_REQUEST = 'INVALID_REQUEST'
    

class LoadBalancer:

    def __init__(self, ip, port, config_path, timeout=2., server_availability_check_period=5.) -> None:
        self.ip = ip 
        self.port = port 
        self.all_servers = self.extract_servers(config_path)
        self.request_queue = Queue()
        self.timeout = timeout
        self.check_period = server_availability_check_period

    def servers_avalability_check(self):
        lock = self.available_servers_lock
        self.available_servers = [] 

        while True:
            if lock.acquire(blocking=True):
                available_servers = set()
                check_threads = []
                server_availability_result = [None] * len(self.all_servers)

                try:
                    for id, server in enumerate(self.all_servers):
                        check_threads.append(threading.Thread(target=self.server_check, name=f"check_t{id}", args=(server_availability_result, id, server,)))
                        check_threads[-1].start()

                    for id, server in enumerate(self.all_servers):
                        check_threads[id].join()

                    for id, server in enumerate(self.all_servers):
                        if server_availability_result[id]:
                            available_servers.add(self.all_servers[id])
                    self.available_servers = list(available_servers)
                    lock.release()
                    time.sleep(self.check_period)
                except Exception as e:
                    print("An error occurred:", e)
                    lock.release()

    def server_check(self, server_availability_result, server_id, server):
        server_ip, server_port = server 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((server_ip, int(server_port)))
                data = RequestType.CONNECTION_TEST.value.encode()
                s.sendall(data)
                data = s.recv(1024).decode().strip()
                
                if data == ResponeType.OK.value:
                    server_availability_result[server_id] = True
                    return 
                server_availability_result[server_id] = False
                return 
            except socket.error:
                server_availability_result[server_id] = False
                return 

    def get_response(self):
        server_index = 0 
        lock = self.available_servers_lock

        while True:
            item = self.request_queue.get()
            if item is None:
                break
            while True:
                if lock.acquire(blocking=True):
                    server_index = min(server_index, len(self.available_servers)-1)
                    prev_server_index = server_index
                    for server_index in [*range(prev_server_index, len(self.available_servers)), *range(0, prev_server_index)]:
                        candidate_server = self.available_servers[server_index]
                        if self.send_request_to_server(candidate_server, item):
                            print(f"request with num={item} is performed by server={candidate_server}")
                            break 
                    else:
                         print(f"all servers are down and request with item={item} is lost")
                    server_index = (server_index+1) % len(self.available_servers)
                    lock.release()
                    break 
            self.request_queue.task_done()

    def send_request_to_server(self, server, item):
        server_ip , server_port = server 
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, int(server_port)))
                data = f"{item}"
                encoded_data = data.encode()
                s.sendall(encoded_data)
                data = s.recv(1024)
                if data.decode().strip() == ResponeType.OK.value:
                    return True 
                return False
        except (socket.timeout, ConnectionRefusedError, ConnectionError) as e:
            return False

    def extract_servers(self, config_path):
        extracted_servers = set()
        pattern = r"\[(\d+\.\d+\.\d+\.\d+)\]\s*\[(\d+)\]"

        with open(config_path, 'r') as f:
            for line in f:
                if line.strip()[0] != '[':
                    continue 
                match = re.search(pattern, line.strip())
                ip, port = match.group(1), match.group(2)
                extracted_servers.add((ip, port))
            return list(extracted_servers)

    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        try:
            with conn:
                while True:
                    data = conn.recv(1024).decode().rstrip()
                    try:    
                        num = int(data)
                        self.request_queue.put(num)
                        conn.sendall(f"{ResponeType.OK.value}\n".encode())
                    except Exception as e:
                        conn.sendall(f"{ResponeType.INVALID_REQUEST.value}\n".encode())
        except Exception as e:
            print(f'connection with {addr} closed')

    def get_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, int(self.port)))
            s.listen()
            print(f"load balancer listening on ({self.ip} , {self.port})")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()


    def start(self):
        self.available_servers_lock = threading.Lock() 
        server_check_thread = threading.Thread(target=self.servers_avalability_check, name="server_check_thread")
        server_check_thread.start()

        get_respone_thread = threading.Thread(target=self.get_response, name="server_get_respone")
        get_respone_thread.start()

        get_request_thread = threading.Thread(target=self.get_request, name="server_get_request")
        get_request_thread.start()

 

# connect_to_server(HOST, PORT)
load_balancer = LoadBalancer(ip, port, config_path)
load_balancer.start()