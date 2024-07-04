# main.py
import sys
from  Router import Router

def main():
    router = Router()
    while True:
        try:
            line = input().strip()
            if not line:
                continue

            parts = line.split()
            command = parts[0]

            if command == "add":
                link_id = int(parts[2])
                neighbor_ip = parts[3]
                distance = int(parts[4])
                router.add_link(link_id, neighbor_ip, distance)

            elif command == "remove":
                link_id = int(parts[2])
                router.remove_link(link_id)

            elif command == "update":
                link_id = int(parts[1])
                vector_length = int(parts[2])
                new_distance_vector = {}
                for _ in range(vector_length):
                    vector_line = input().strip().split()
                    ip = vector_line[0]
                    distance = int(vector_line[1])
                    new_distance_vector[ip] = distance
                router.update_distance_vector(link_id, new_distance_vector)

            elif command == "print":
                router.print_distance_vector()

            elif command == "route":
                destination_ip = parts[1]
                router.route_packet(destination_ip)

            elif command == "exit":
                break

        except EOFError:
            break

if __name__ == "__main__":
    main()
