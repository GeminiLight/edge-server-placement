import time

from algo.random import *
from algo.kmeans import *
from algo.mlp import *
from algo.random import *
from algo.weighted_kmeans import *
from algo.topk import *
from utils import *


def run_problem(problem, n, k):
    
    return 


def run_with_parameters(placer, n, k, repeat_times=1):
    if repeat_times == 1:
        placer.place_server(n, k)
        res = placer.objective_latency(), placer.objective_workload()
    else:
        sum_a = 0
        sum_b = 0
        for t in range(repeat_times):
            placer.place_server(n, k)
            res = placer.objective_latency(), placer.objective_workload()
            sum_a += res[0]
            sum_b += res[1]
            time.sleep(1)
        res = (sum_a / 10, sum_b / 10,)
    return res


def run(placers):
    with open('results/results.txt', 'w') as file:
        # 第一个图
        # for n in range(300, 3300, 300):
        #     k = int(n / 10)
        #     print("N={0}, K={1}".format(n, k), file=file)
        #     results = run_with_parameters(problems, n, k)
        #     for key, value in results.items():
        #         print(key, "平均距离(km)={0}, 负载标准差={1}".format(value[0], value[1]), file=file)
        #         file.flush()
        #
        # print("======================================================", file=file)

        # 第二个图
        n = 3000
        for k in range(100, 600, 100):
            print("N={0}, K={1}".format(n, k), file=file)
            results = {}
            for name, placer in placers.items():
                result = run_with_parameters(placer, n, k)
                results[name] = result
            for key, value in results.items():
                print(key, "平均距离(km)={0}, 负载标准差={1}".format(value[0], value[1]), file=file)
                file.flush()
        file.close()


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