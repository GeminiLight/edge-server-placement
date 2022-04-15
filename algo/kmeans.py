import logging
from datetime import datetime
from typing import List, Iterable

import numpy as np
import scipy.cluster.vq as vq
from sklearn.cluster import KMeans

from data.edge_server import EdgeServer

from .server_placer import ServerPlacer


class KMeansServerPlacer(ServerPlacer):
    """
    K-means approach
    """
    name = 'KMeans'
    def place_server(self, base_station_num, edge_server_num):
        logging.info("{0}:Start running k-means with N={1}, K={2}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                          base_station_num, edge_server_num))
        # init data as ndarray
        base_stations = self.base_stations[:base_station_num]
        coordinates = list(map(lambda x: (x.latitude, x.longitude), base_stations))
        data = np.array(coordinates)
        k = edge_server_num

        # k-means
        kmeans = KMeans(n_clusters=k, random_state=0, max_iter=100).fit(data)
        centroid = kmeans.cluster_centers_
        label = kmeans.labels_

        # process result
        edge_servers = [EdgeServer(i, row[0], row[1]) for i, row in enumerate(centroid)]
        for bs, es in enumerate(label):
            edge_servers[es].assigned_base_stations.append(base_stations[bs])
            edge_servers[es].workload += base_stations[bs].workload

        self.edge_servers = list(filter(lambda x: x.workload != 0, edge_servers))
        logging.info("{0}:End running k-means".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
