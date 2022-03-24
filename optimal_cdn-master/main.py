import argparse

from client import ClientManager
from server import ServerManager
from placement_algorithms import placement, optimal_placement

"""
Call main.py from the command line, specifying the input and output files as arguments.
e.g. python3 main.py input_1.txt result.txt
"""

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_name", type=str, help="Input file name")
    parser.add_argument("output_name", type=str, help="Output file name")
    args = parser.parse_args()
    return args.input_name, args.output_name

def read_input(file_name):
    """
    Input: file name (string).
    File format:
        int algorithm (1 or 2)
        int number of servers
        list of int [client demands]
    Reads file and outputs a list of clients, a list of servers and the algorithm.
    """
    f = open(file_name, 'r')
    client_manager = ClientManager()
    server_manager = ServerManager()
    algorithm = int(f.readline())
    number_servers = int(f.readline())
    servers = [server_manager.create_server() for i in range(number_servers)]
    demands = map(int, f.readline().split())
    clients = [client_manager.create_client(demand) for demand in demands]
    return clients, servers, algorithm

def write_output(file_name, placement_manager):
    """
    Write result from placement algorithm into specified file.
    """
    f = open(file_name, 'w')
    for server in placement_manager.servers:
        served_clients = placement_manager.get_clients_served_by(server)
        f.write("Server {}, used capacity = {:f}\n".format(server.id, server.used_capacity))
        f.write("Client ids: " + " ".join([str(client.id) for client in served_clients]) + "\n")
        f.write("Client demands: " + " ".join([str(client.demand) for client in served_clients]) + "\n")
        f.write("########################################################################\n")


if __name__ == '__main__':
    input_name, output_name = parse_args()
    clients, servers, algorithm = read_input(input_name)
    placement_algorithm = placement if algorithm==1 else optimal_placement
    placement_manager = placement_algorithm(clients, servers)
    write_output(output_name, placement_manager)



