class PlacementManager(object):

    """
    Manages client placement into servers.
    """

    def __init__(self, servers_):
        """
        Initialized from a list of servers and no clients.
        """
        self.servers = servers_
        # Each client maps to a list of tuples (servers, multiplicative_factor),
        # since for each client the order of servers matters.
        self.__map_client_servers = {}
        # Each server maps to a to a map of {client : multiplicative_factor}.
        self.__map_server_clients = {server : {} for server in self.servers}

    def place_client(self, client, server):
        """
        Place a client into a single server, with multiplicative_factor 1.0.
        Update server's used_capacity and insert client into dictionaries.
        """
        server.used_capacity += client.demand
        self.__map_client_servers[client] = [(server, 1.0)]
        self.__map_server_clients[server][client] = 1.0

    def get_clients_served_by(self, server):
        return self.__map_server_clients[server]

    def get_servers(self, client):
        return self.__map_client_servers[client]

    def reset(self, clients):
        """
        Deallocate clients from servers.
        """
        for client in clients:
            self.__map_client_servers[client] = []

    def set_multiplicative_factor(self, server, clients, multiplicative_factor):
        """
        Change multiplicative_factor for a list of clients and a single host.
        """
        for client in clients:
            self.__map_client_servers[client].append((server, multiplicative_factor))
            self.__map_server_clients[server][client] = multiplicative_factor

