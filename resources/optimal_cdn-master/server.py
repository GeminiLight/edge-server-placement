class Server(object):

    """
    Server class with two fields: id and used_capacity, the sum of the clients' demands using the server.
    """

    def __init__(self, id_):
        self.id = id_
        self.used_capacity = 0.0

    def __lt__(self, other):
        """
        Used for sorting.
        """
        return self.used_capacity < other.used_capacity

class ServerManager(object):

    """
    Servers are not created directly.
    Rather generated from the ServerManager create_server method.
    """

    def __init__(self):
        self.__latest_id = 0

    def create_server(self):
        self.__latest_id += 1
        return Server(self.__latest_id)
