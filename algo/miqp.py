import cplex
import logging
import random
import numpy as np
from datetime import datetime

from algo.server_placer import ServerPlacer
from data.edge_server import EdgeServer


class MIQPServerPlacer(ServerPlacer):
    """
    MIQP base heuristic
    """
    name = 'MIQP'
    def __init__(self, base_stations, distances):
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
