import time

from sklearn.utils import resample

from algo.random import *
from algo.kmeans import *
from algo.mlp import *
from algo.random import *
from algo.weighted_kmeans import *
from algo.topk import *
from utils import *


def run_with_settings(placer, n, k, repeat_times=1):
    if repeat_times == 1:
        placer.place_server(n, k)
        objectives = placer.compute_objectives()
    else:
        # run multiple times to obtain the mean value
        objectives_list = []
        for t in range(repeat_times):
            placer.place_server(n, k)
            one_objectives = placer.compute_objectives()
            time.sleep(1)
            objectives_list.append(one_objectives)

        objectives = {}
        for k in objectives_list[-1].keys():
            mean_value = sum(o[k] for o in objectives_list) / len(objectives_list)
            objectives[k] = mean_value
    return objectives


def run(placers, results_fpath='results/results.csv'):
    n = 3000
    records = []
    for k in range(100, 600, 100):
        print(f'\nSettings: N={n}, K={k}')
        for name, placer in placers.items():
            settings = {'num_base_stations': n, 'num_edge_servers': k, 'placer_name': name}
            objectives = run_with_settings(placer, n, k)
            record = {**settings, **objectives}
            records.append(record)
    pd_records = pd.DataFrame(records)
    pd_records.to_csv(results_fpath)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    data = DataUtils('./dataset/base_stations_min.csv', './dataset/data_min.csv')
    placers = {}
    # placers['MIP'] = MIPServerPlacer(data.base_stations, data.distances)
    placers['K-means'] = KMeansServerPlacer(data.base_stations, data.distances)
    placers['Top-K'] = TopKServerPlacer(data.base_stations, data.distances)
    placers['Random'] = RandomServerPlacer(data.base_stations, data.distances)
    placers['weighted_k_means'] = WeightedKMeansServerPlacer(data.base_stations, data.distances)
    run(placers)