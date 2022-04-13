import unittest
import random

from placement import PlacementManager
from server import ServerManager
from client import ClientManager


class TestPlacementManager(unittest.TestCase):

    """
    Unittests for PlacementManager class.
    """

    def test_place_and_get_zero_clients(self):
        """
        Servers are initialized empty.
        """
        server_manager = ServerManager()
        servers = [server_manager.create_server() for i in range(30)]
        placement_manager = PlacementManager(servers)
        for server in servers:
            self.assertEqual(placement_manager.get_clients_served_by(server), {})

    def test_place_in_single_server(self):
        """
        All clients served by a single server.
        Its used capacity equals the total client demand.
        """
        server_manager = ServerManager()
        client_manager = ClientManager()
        server = server_manager.create_server()
        number_clients = 100
        demands = [random.randint(10, 30) for i in range(number_clients)]
        clients = [client_manager.create_client(demand) for demand in demands]
        placement_manager = PlacementManager([server])
        for client in clients:
            placement_manager.place_client(client, server)
        for client in clients:
            self.assertEqual(placement_manager.get_servers(client), [(server, 1.0)])
        self.assertEqual(placement_manager.get_clients_served_by(server),
                          {client : 1.0 for client in clients})
        self.assertEqual(server.used_capacity, sum(demands))

    def test_place_in_multiple_servers(self):
        """
        Each client placed in a server, with multiplicative_factor one.
        For each server, the used capacity equals the sum of its clients' demands.
        """
        number_servers = 30
        number_clients = 1000
        server_manager = ServerManager()
        client_manager = ClientManager()
        servers = [server_manager.create_server() for i in range(number_servers)]
        clients = [client_manager.create_client(random.randint(10, 30)) for i in range(number_clients)]
        placement_manager = PlacementManager(servers)
        server = 0
        for client in clients:
            placement_manager.place_client(client, servers[server])
            server = (server+1)%number_servers
        for i in range(number_clients):
            self.assertEqual(placement_manager.get_servers(clients[i]), [(servers[i%number_servers], 1.0)])
        for i in range(number_servers):
            served_clients = [clients[j] for j in range(i, number_clients, number_servers)]
            self.assertEqual(placement_manager.get_clients_served_by(servers[i]),
                             {client : 1.0 for client in served_clients})
            self.assertEqual(servers[i].used_capacity,
                             sum(client.demand for client in served_clients))

    def test_set_multiplicative_factors(self):
        """
        Place each clients i in two servers:
        server[0], with multiplicative_factor k, and servers[1] with multiplicative_factor 1.0-k.
        """
        number_servers = 2
        number_clients = 1000
        server_manager = ServerManager()
        client_manager = ClientManager()
        servers = [server_manager.create_server() for i in range(number_servers)]
        clients = [client_manager.create_client(random.randint(10, 30)) for i in range(number_clients)]
        placement_manager = PlacementManager(servers)
        multiplicative_factors = [random.random() for i in range(number_clients)]
        for i in range(number_clients):
            placement_manager.reset(clients[i:i+1])
            placement_manager.set_multiplicative_factor(servers[0], clients[i:i+1], multiplicative_factors[i])
            placement_manager.set_multiplicative_factor(servers[1], clients[i:i+1], 1.0 - multiplicative_factors[i])
        for i in range(number_clients):
            retrieved_servers = placement_manager.get_servers(clients[i])
            self.assertEqual(retrieved_servers[0][1], multiplicative_factors[i])
            self.assertEqual(retrieved_servers[1][1], 1.0 - multiplicative_factors[i])
        retrieved_clients = placement_manager.get_clients_served_by(servers[0])
        self.assertEqual(retrieved_clients,
                          {clients[i] : multiplicative_factors[i] for i in range(number_clients)})
        retrieved_clients = placement_manager.get_clients_served_by(servers[1])
        self.assertEqual(retrieved_clients,
                          {clients[i] : 1.0 - multiplicative_factors[i] for i in range(number_clients)})


if __name__ == '__main__':
    unittest.main()
