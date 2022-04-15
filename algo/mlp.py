import math
import logging
from datetime import datetime
from typing import List, Iterable

import cplex

import numpy as np
import scipy.cluster.vq as vq

from data.base_station import BaseStation
from data.edge_server import EdgeServer
from .server_placer import ServerPlacer


class MIPServerPlacer(ServerPlacer):
    """
    MIP approach
    """
    name = 'MIP'
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
        self.n = base_station_num if base_station_num <= len(self.base_stations) else len(self.base_stations)
        self.k = edge_server_num

        self.preprocess_problem()

        c = cplex.Cplex()

        # c.parameters.mip.limits.nodes.set(50000)

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
        # For each base station, find the closest N/K base stations
        d = np.array([row[:self.n] for row in self.distances[:self.n]])
        cap = int(len(base_stations) / self.k)
        assign = []
        # distance
        max_distances = []
        for i, row in enumerate(d):
            indices = row.argpartition(cap)[:cap]
            assign.append(indices)
            t = row[indices]
            max_distances.append(row[indices].max())
            logging.debug("Found nearest {0} base stations of base station {1}".format(cap, i))
        # workload
        avg_workload = sum((item.workload for item in base_stations)) / self.k
        workload_diff = []
        for row in assign:
            assigned_stations = (base_stations[item] for item in row)
            workload = sum((item.workload for item in assigned_stations))
            expr = math.pow(workload - avg_workload, 2)
            workload_diff.append(expr)

        # normalization
        normalized_max_distances = MIPServerPlacer._normalize(max_distances)
        normalized_workload_diff = MIPServerPlacer._normalize(workload_diff)

        
        # belongs: find the neighbors of base staion to place edge servers so that each base staions can be considerd
        belongs = [[] for i in range(self.n)]  
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

        # constraint: whether a base staion has been assigned to a edge server
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

        # constraint:  the total number of edge server that has been assigned
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