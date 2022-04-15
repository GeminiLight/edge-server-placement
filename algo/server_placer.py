import logging
from datetime import datetime
from typing import List, Iterable

import numpy as np

from data.base_station import BaseStation
from data.edge_server import EdgeServer
from utils import DataUtils



class ServerPlacer(object):
    def __init__(self, base_stations: List[BaseStation], distances: List[List[float]]):
        self.base_stations = base_stations.copy()
        self.edge_servers = None
        self.distances = distances

    def place_server(self, base_station_num, edge_server_num):
        raise NotImplementedError

    def _distance_edge_server_base_station(self, edge_server: EdgeServer, base_station: BaseStation) -> float:
        """
        Calculate distance between given edge server and base station
        
        :param edge_server: 
        :param base_station: 
        :return: distance(km)
        """
        if edge_server.base_station_id:
            return self.distances[edge_server.base_station_id][base_station.id]
        return DataUtils.calc_distance(edge_server.latitude, edge_server.longitude, base_station.latitude,
                                       base_station.longitude)

    def compute_objectives(self):
        objectives = {
            'latency': self.objective_latency(), 
            'workload': self.objective_workload()
        }
        return objectives

    def objective_latency(self):
        """
        Calculate average edge server access delay (Average distance(km))
        """
        assert self.edge_servers
        total_delay = 0
        base_station_num = 0
        for es in self.edge_servers:
            for bs in es.assigned_base_stations:
                delay = self._distance_edge_server_base_station(es, bs)
                logging.debug("base station={0}  delay={1}".format(bs.id, delay))
                total_delay += delay
                base_station_num += 1
        return total_delay / base_station_num

    def objective_workload(self):
        """
        Calculate average edge server workload (Load standard deviation)
        
        Max worklaod of edge server - Min workload
        """
        assert self.edge_servers
        workloads = [e.workload for e in self.edge_servers]
        logging.debug("standard deviation of workload" + str(workloads))
        res = np.std(workloads)
        return res