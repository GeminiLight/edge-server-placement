import logging
import math
import random
from datetime import datetime
from typing import List, Iterable

import cplex
import numpy as np
import scipy.cluster.vq as vq

from base_station import BaseStation
from edge_server import EdgeServer
from utils import DataUtils


class ServerPlacer(object):
    def __init__(self, base_stations: List[BaseStation], distances: List[List[float]]):
        self.base_stations = base_stations.copy()
        self.distances = distances
        self.edge_servers = None

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

    def objective_latency(self):
        """
        Calculate average edge server access delay
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
        Calculate standar deviations of edge server workload
        
        Max worklaod of edge server - Min workload
        """
        assert self.edge_servers
        workloads = [e.workload for e in self.edge_servers]
        logging.debug("standard deviation of workload" + str(workloads))
        res = np.std(workloads)
        return res


class KMeansServerPlacer(ServerPlacer):
    """
    K-means approach
    """

    def place_server(self, base_station_num, edge_server_num):
        logging.info("{0}:Start running k-means with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                          base_station_num, edge_server_num))
        # init data as ndarray
        base_stations = self.base_stations[:base_station_num]
        coordinates = list(map(lambda x: (x.latitude, x.longitude), base_stations))
        data = np.array(coordinates)
        k = edge_server_num

        # k-means
        centroid, label = vq.kmeans2(data, k, iter=100)

        # process result
        edge_servers = [EdgeServer(i, row[0], row[1]) for i, row in enumerate(centroid)]
        for bs, es in enumerate(label):
            edge_servers[es].assigned_base_stations.append(base_stations[bs])
            edge_servers[es].workload += base_stations[bs].workload

        self.edge_servers = list(filter(lambda x: x.workload != 0, edge_servers))
        logging.info("{0}:End running k-means".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


class TopKServerPlacer(ServerPlacer):
    """
    Top-K approach
    """

    def place_server(self, base_station_num, edge_server_num):
        logging.info("{0}:Start running Top-k with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                        base_station_num, edge_server_num))
        base_stations = self.base_stations[:base_station_num]
        sorted_base_stations = sorted(base_stations, key=lambda x: x.workload, reverse=True)
        edge_servers = [EdgeServer(i, item.latitude, item.longitude, item.id) for i, item in
                        enumerate(sorted_base_stations[:edge_server_num])]
        for i, base_station in enumerate(sorted_base_stations):
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
        logging.info("{0}:End running Top-k".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


class RandomServerPlacer(ServerPlacer):
    """
    Random approach
    """

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


class MIQPServerPlacer(ServerPlacer):
    """
    MIQP base heuristic
    """

    def __init__(self, base_stations: List[BaseStation], distances: List[List[float]]):
        super().__init__(base_stations, distances)
        self.n = 0
        self.k = 0
        self.workloads = np.array([bs.workload for bs in base_stations])
        self.avg_workload = None
        self.ln_coefs = None
        self.qmat = None
        self.dvars = None

    def place_server(self, base_station_num, edge_server_num):
        logging.info("{0}:Start running MIQP with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                       base_station_num, edge_server_num))

        self.n = base_station_num
        self.k = edge_server_num
        distances = np.array([self.distances[i][:self.n] for i in range(self.n)])

        self.preprocess()

        locations = [1] * self.k + [0] * (self.n - self.k)
        random.shuffle(locations)

        c = self.setup_problem(locations)
        c.solve()
        print(c.solution.get_objective_value())
        solutions = np.array(
            [[int(c.solution.get_values('x_{0}_{1}'.format(i, l))) for l in range(self.n)] for i in range(self.n)])

        # new locations
        while True:
            centers = [0] * self.n
            for l, v in enumerate(locations):
                if v == 1:
                    min_dist = 1e10
                    position = None
                    mask = solutions[:, l]
                    if mask.sum() == 0:
                        logging.warning("empty edge server!!!!!!!!!!!!!!!!")
                        centers[l] = 1
                        continue

                    for ind, v in enumerate(mask):
                        if v == 1:
                            t = np.sum(distances[ind] * mask)
                            if t < min_dist:
                                min_dist = t
                                position = ind

                    centers[position] = 1

            if False not in [x == y for x, y in zip(centers, locations)]:
                self.process_result(solutions, locations)
                break

            locations = centers
            c = self.setup_problem(locations)
            c.solve()
            print(c.solution.get_objective_value())
            solutions = np.array(
                [[int(c.solution.get_values('x_{0}_{1}'.format(i, l))) for l in range(self.n)] for i in range(self.n)])

        logging.info("{0}:End running MIQP".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        pass

    def preprocess(self):
        mu = 0.5
        self.dvars = ['x_{0}_{1}'.format(i, j) for i in range(self.n) for j in range(self.n)]

        wl = self.workloads[:self.n]
        assert isinstance(wl, np.ndarray)
        dist_ln = np.array([self.distances[i][j] for i in range(self.n) for j in range(self.n)])
        wl_ln = np.array([self.workloads[i] for i in range(self.n) for j in range(self.n)])

        avg_workload = np.average(wl)
        wb_max = np.var([np.sum(wl)] + [0] * (self.k - 1))
        dist_max = self.n * np.max(dist_ln)

        ln_coefs = -2 * mu * wl_ln * avg_workload / self.k / wb_max + (1 - mu) * dist_ln / dist_max
        self.ln_coefs = ln_coefs

        qua_coefs = np.dot(wl.reshape((self.n, 1)), wl.reshape((1, self.n))) / self.k / wb_max
        qmat = []
        for i in range(self.n):
            for row in range(self.n):
                t = [list(range(i * self.n, (i + 1) * self.n)), qua_coefs[row].tolist()]
                qmat.append(t)
        self.qmat = qmat

    def setup_problem(self, locations):
        c = cplex.Cplex()
        c.objective.set_sense(c.objective.sense.minimize)

        # decision variables
        # linear part of objective function
        c.variables.add(names=self.dvars, ub=[1] * len(self.dvars), lb=[0] * len(self.dvars),
                        types=['B'] * len(self.dvars),
                        obj=self.ln_coefs)

        # quadratic part of objective function
        c.objective.set_quadratic(self.qmat)

        # constraint: for each i, sum xi, l == 1
        for i in range(self.n):
            varnames = ['x_{0}_{1}'.format(i, l) for l in range(self.n)]
            c.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=varnames, val=[1] * len(varnames))],
                senses=["E"], rhs=[1])

        # constraint: for each l xi,l <= yl
        for l, y in enumerate(locations):
            for i in range(self.n):
                c.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=['x_{0}_{1}'.format(i, l)], val=[1])],
                                         senses=["L"], rhs=[y])

        return c

    def process_result(self, solution, locations):
        base_stations = self.base_stations[:self.n]
        positions = [l for l, i in enumerate(locations) if i == 1]
        edge_servers = [EdgeServer(i, base_stations[x].latitude, base_stations[x].longitude, base_stations[x].id) for
                        i, x in enumerate(positions)]
        for i, p in enumerate(positions):
            for j in range(self.n):
                if solution[j][p] == 1:
                    edge_servers[i].assigned_base_stations.append(base_stations[j])
                    edge_servers[i].workload += base_stations[j].workload
        self.edge_servers = edge_servers
