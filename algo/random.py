import random
import logging
from datetime import datetime

from algo.server_placer import ServerPlacer
from data.base_station import BaseStation
from data.edge_server import EdgeServer


class RandomServerPlacer(ServerPlacer):
    """
    Random approach
    """
    name = 'Random'
    def place_server(self, base_station_num, edge_server_num):
        base_stations = self.base_stations[:base_station_num]
        logging.info("{0}:Start running Random with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                         base_station_num, edge_server_num))
        random_base_stations = random.sample(self.base_stations, edge_server_num)
        edge_servers = [EdgeServer(i, item.latitude, item.longitude, item.id) for i, item in
                        enumerate(random_base_stations)]
        for i, base_station in enumerate(base_stations):
            closest_edge_server = None
            min_distance = 1e10
            for j, edge_server in enumerate(edge_servers):
                tmp = self._distance_edge_server_base_station(edge_server, base_station)
                if tmp < min_distance:
                    min_distance = tmp
                    closest_edge_server = edge_server
            closest_edge_server.assigned_base_stations.append(base_station)
            closest_edge_server.workload += base_station.workload
        self.edge_servers = edge_servers
        logging.info("{0}:End running Random".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))