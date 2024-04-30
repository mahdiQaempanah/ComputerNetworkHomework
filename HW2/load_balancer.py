import socket
import threading
import os
from queue import Queue
import re 
import time 

config_path = './config'
ip = "127.0.0.1"
port = 65432

class LoadBalancer:
    def __init__(self, config_path, timeout=2., server_availability_check_period=1) -> None:
        self.all_servers = self.extract_servers(config_path)
        self.timeout = timeout
        self.check_period = server_availability_check_period


    def servers_avalability_check(self):
        lock = self.available_servers_lock

        while True:
            if lock.acquire(blocking=True):
                available_servers = set()
                check_threads = []
                return_values = [None] * len(self.all_servers)

                try:
                    for id, server in enumerate(self.all_servers):
                        check_threads.append(threading.Thread(target=self.server_check, name=f"check_t{id}", args=(server,)))
                        check_threads[-1].start()

                    for id, server in enumerate(self.all_servers):
                        check_threads[id].join()

                    for id, server in enumerate(self.all_servers):
                        if return_values[id]:
                            available_servers.add(self.all_servers[id])
                    self.available_servers = list(available_servers)
                    lock.release()
                    time.sleep(self.check_period)
                except Exception as e:
                    print("An error occurred:", e)
                    lock.release()

    
    def server_check(self, server) -> bool:
        server_ip, server_port = server 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((server_ip, server_port))
                s.sendall(b"connection_check")
                data = s.recv(1024).decode().strip()
                if data == "Server is alive":
                    return True
                return False 
            except socket.error:
                return False
            

    def connect_to_server(self, host, port, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"Hello, world")
            data = s.recv(1024)
        print(f"Received {data!r}")

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
                        if self.send_request(candidate_server, item):
                            print(f"request with item={item} is performed by server={candidate_server}")
                            break 
                    else:
                         print(f"all servers are down and request with item={item} is lost")
                    server_index = (server_index+1) % len(self.available_servers)
                    lock.release()
                    break 
            self.request_queue.task_done()

    def send_request(self, server, item):
        server_ip , server_port = server 
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((server_ip, server_ip))
                data = f"{item}"
                encoded_data = data.encode()
                s.sendall(encoded_data)
                data = s.recv(1024)
                if data.decode() == "OK":
                    s.close()
                    return True 
                else:
                    return False
        except (socket.timeout, ConnectionRefusedError, ConnectionError) as e:
            # print(f"Error: {e}")
            return False


    def start(self):
        self.available_servers_lock = threading.Lock() 
        server_check_thread = threading.Thread(target=self.servers_avalability_check, name="server_check_thread")
        server_check_thread.start()

        get_respone_thread = threading.Thread(target=self.get_response, name="server_get_respone")
        get_respone_thread.start()

        self.request_queue = Queue()
        self.request_queue.ta
        while True:
            num = input().rstrip()
            try:
                num = int(num)
            except Exception as e:
                print("invalid input. you must send only one number to get your response.")
            self.request_queue.put(num)

    def extract_servers(self, config_path):
        extracted_servers = set()
        pattern = r"\[(\d+\.\d+\.\d+\.\d+)\]\s*\[(\d+)\]"

        with open(config_path, 'r') as f:
            for line in f:
                match = re.search(pattern, line.rstrip())
                ip, port = match.group(1), match.group(2)
                extracted_servers.add((ip, port))
            return list(extracted_servers)

    

# connect_to_server(HOST, PORT)
LoadBalancer(config_path).start()