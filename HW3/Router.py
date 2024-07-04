from collections import defaultdict
from ipaddress import IPv4Address, IPv4Network


class Neighbor:
    def __init__(self, subnet, distance) -> None:
        self.subnet = subnet
        self.link_distance = distance
        self.distance_vector = {}

class Router:
    def __init__(self):
        self.links = {}

    def is_member(self, subnet, ip):
        return IPv4Address(ip) in IPv4Network(subnet)

    def add_link(self, link_id, neighbor_subnet, distance):
        nbr = Neighbor(neighbor_subnet, distance)
        self.links[link_id] = nbr 

    def remove_link(self, link_id):
        if link_id in self.links.keys():
            self.links.pop(link_id)

    def update_distance_vector(self, link_id, new_distance_vector):
        nbr = self.links[link_id]
        nbr.distance_vector = {}
        for subnet, distance in new_distance_vector.items():
            nbr.distance_vector[subnet] = distance

    def print_distance_vector(self):
        self.distance_vector = self.calculate_distance_vector()
        for ip in sorted(self.distance_vector.keys()):
            print(f"{ip} {self.distance_vector[ip]}")
        
    def calculate_distance_vector(self):
        ret = defaultdict(lambda: float('inf'))
        for link_id, link in self.links.items():
            ret[link.subnet] = min(ret[link.subnet], link.link_distance)
            for subnet, distance in link.distance_vector.items():
                ret[subnet] = min(ret[subnet], link.link_distance + distance)
        return ret

    def route_packet(self, destination_ip):
        answer = [-1, float('inf')]
        for link_id, link in self.links.items():
            if self.is_member(link.subnet, destination_ip) and link.link_distance < answer[1]:
                answer = [link_id, link.link_distance ]
            for subnet, distance in link.distance_vector.items():
                if self.is_member(subnet, destination_ip) and link.link_distance + distance < answer[1]:
                    answer = [link_id, link.link_distance + distance]
        if answer[0] == -1:
            print("No route found")
        else:
            print(answer[0])
