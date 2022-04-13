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
        Calculate average edge server workload
        
        Max worklaod of edge server - Min workload
        """
        assert self.edge_servers
        workloads = [e.workload for e in self.edge_servers]
        logging.debug("standard deviation of workload" + str(workloads))
        res = np.std(workloads)
        return res


class MIPServerPlacer(ServerPlacer):
    """
    MIP approach
    """

    def __init__(self, base_stations: List[BaseStation], distances: List[List[float]]):
        super().__init__(base_stations, distances)
        self.n = 0
        self.k = 0
        self.weights = None
        self.belongs = None
        self.assgin = None
        self.placement_vars = None
        self.assigned_vars = None

    def place_server(self, base_station_num, edge_server_num):
        logging.info("{0}:Start running MIP with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                      base_station_num, edge_server_num))
        self.n = base_station_num
        self.k = edge_server_num

        self.preprocess_problem()

        c = cplex.Cplex()

        c.parameters.mip.limits.nodes.set(5000)

        self.setup_problem(c)

        c.solve()

        assert self.placement_vars
        assert self.assigned_vars
        solution = c.solution
        if solution.is_primal_feasible():
            print("Solution value = ", solution.get_objective_value())
            solution_vars = [solution.get_values(var) for var in self.placement_vars]
            assigned_vars = [solution.get_values(var) for var in self.assigned_vars]
            places = [i for i, x in enumerate(solution_vars) if x == 1]
            print(places)
            print(assigned_vars)
            self.process_result(places)
        else:
            print("No solution available")
        logging.info("{0}:End running MIP".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def preprocess_problem(self):
        base_stations = self.base_stations[:self.n]
        # 每个基站，找出距离它最近的N/K个基站
        d = np.array([row[:self.n] for row in self.distances[:self.n]])
        cap = int(len(base_stations) / self.k)
        assign = []
        max_distances = []  # 距离
        for i, row in enumerate(d):
            indices = row.argpartition(cap)[:cap]
            assign.append(indices)
            t = row[indices]
            max_distances.append(row[indices].max())
            logging.debug("Found nearest {0} base stations of base station {1}".format(cap, i))

        # 负载
        avg_workload = sum((item.workload for item in base_stations)) / self.k
        workload_diff = []
        for row in assign:
            assigned_stations = (base_stations[item] for item in row)
            workload = sum((item.workload for item in assigned_stations))
            expr = math.pow(workload - avg_workload, 2)
            workload_diff.append(expr)

        # 归一化
        normalized_max_distances = MIPServerPlacer._normalize(max_distances)
        normalized_workload_diff = MIPServerPlacer._normalize(workload_diff)

        belongs = [[] for i in range(self.n)]  # belongs: 表示一个基站要被照顾到，可以在那些地方部署边缘服务器
        for i, row in enumerate(assign):
            for bs in row:
                belongs[bs].append(i)

        alpha = 0.5
        self.weights = [alpha * normalized_max_distances[i] + (1 - alpha) * normalized_workload_diff[i] for i in
                        range(self.n)]
        self.belongs = belongs
        self.assign = assign

        pass

    def setup_problem(self, c: cplex.Cplex):
        assert self.weights
        assert self.belongs

        c.objective.set_sense(c.objective.sense.minimize)

        # placement variables: placement[i] = 1 if a edge server is placed with base station i
        placement_vars = []
        for i in range(self.n):
            varname = "place_{0}".format(i)
            placement_vars.append(varname)
        c.variables.add(obj=self.weights, names=placement_vars, lb=[0] * len(placement_vars),
                        ub=[1] * len(placement_vars),
                        types=[c.variables.type.binary] * len(placement_vars))

        # assigned variables: assigned[i] = 1 if base station i has been assigned to at least one edge server
        assigned_vars = []
        for i in range(self.n):
            varname = "assigned_{0}".format(i)
            assigned_vars.append(varname)
        c.variables.add(names=assigned_vars, lb=[0] * len(assigned_vars), ub=[1] * len(assigned_vars),
                        types=[c.variables.type.binary] * len(assigned_vars))

        # constraint: total number of edge servers should be K
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(placement_vars, [1 for i in range(self.n)])],
                                 senses=['E'], rhs=[self.k])

        # constraint: assigned 表示是否为基站分配了边缘服务器
        # assigned[i] >= all place[j] for j in belongs[i]
        for bsid, esids in enumerate(self.belongs):
            varnames = []
            coefficients = []
            assigned_varname = "assigned_{0}".format(bsid)
            for esid in esids:
                place_varname = "place_{0}".format(esid)
                varnames.append(place_varname)
                coefficients.append(1)
                c.linear_constraints.add(lin_expr=[cplex.SparsePair([assigned_varname, place_varname], [1, -1])],
                                         senses=['G'], rhs=[0])
            varnames.append(assigned_varname)
            coefficients.append(-1)
            c.linear_constraints.add(lin_expr=[cplex.SparsePair(varnames, coefficients)],
                                     senses=['G'], rhs=[0])

        # constraint: 被分配了边缘服务器的基站的总数
        acceptable = int(self.n * 0.9)
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(assigned_vars, [1 for i in range(self.n)])],
                                 senses=['G'], rhs=[acceptable])

        self.assigned_vars = assigned_vars
        self.placement_vars = placement_vars

    def process_result(self, solution):
        """
        :param solution: a list containing all id of base stations selected to put an edge server with it
        :return: 
        """
        base_stations = self.base_stations[:self.n]
        edge_servers = [EdgeServer(i, base_stations[x].latitude, base_stations[x].longitude, base_stations[x].id)
                        for i, x in enumerate(solution)]
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

    @staticmethod
    def _normalize(l: Iterable):
        minimum = min(l)
        delta = max(l) - minimum
        return [(i - minimum) / delta for i in l]


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
