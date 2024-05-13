import telnetlib 
import re
import subprocess
import time

config_path = './config'
ip = "127.0.0.1"
port = 65430

def run_servers(config_path):
    servers = set()
    pattern = r"\[(\d+\.\d+\.\d+\.\d+)\]\s*\[(\d+)\]"
    with open(config_path, 'r') as f:
        for line in f:
            if line.strip()[0] != '[':
                continue 
            match = re.search(pattern, line.strip())
            ip, port = match.group(1), match.group(2)
            try:
                server = subprocess.Popen(["python3", 'server.py', ip, str(port)])
                servers.add((server, ip, port))
            except subprocess.CalledProcessError:
                print(f"Error: Failed to run server={ip}:{port}")
    return servers

def kill_servers(servers):
    for server in servers:
        server[0].kill()

def test_server(ip, port):
    try:
        tn = telnetlib.Telnet(ip, port)
        for i in range(1000):
            tn.write(f"{i}\n".encode())
            response = tn.read_until(b"\n").decode().strip()
    except Exception as e:
        print("An error occurred:", e)

def usage_of_servers(servers):
    server_call_count = {(str(server[1]), str(server[2])): 0 for server in servers}
    with open('test-log.txt', 'r') as f:
        for line in f:
            line = line.strip()
            #f"request with num={item} and addr={addr} is performed by server=({candidate_server.ip}, {candidate_server.port})")
            pattern = r"request with num=(\d+) and addr=\((\'\d+\.\d+\.\d+\.\d+)\', (\d+)\) is performed by server=\((\d+\.\d+\.\d+\.\d+), (\d+)\)"
            match = re.search(pattern, line)
            if match:
                item, addr_ip, addr_port, server_ip, server_port = match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)
                server_call_count[(str(server_ip), str(server_port))] += 1
    for server in server_call_count:
        print(f"server={server} is called {server_call_count[server]} times")
                

def test():
    with open('test-log.txt', 'w') as file:
        file.truncate(0)

    with open('test-log.txt', 'w') as log_file:
        load_balancer = subprocess.Popen(["python3", 'load_balancer.py'], stdout=log_file)
        time.sleep(1)
        servers = run_servers(config_path)
        time.sleep(2)
        test_server(ip, port)
        time.sleep(2)
        load_balancer.kill()
        kill_servers(servers)
        usage_of_servers(servers)


test()