import unittest
import random

from client import ClientManager


class TestClientManager(unittest.TestCase):

    def test_create_clients(self):
        number_clients = 100
        demands = [random.randint(1, 100) for i in range(number_clients)]
        client_manager = ClientManager()
        clients = [client_manager.create_client(demand) for demand in demands]
        for i in range(number_clients):
            self.assertEqual(clients[i].id, i+1)
            self.assertEqual(clients[i].demand, demands[i])


if __name__ == '__main__':
    unittest.main()
