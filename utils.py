import random
import csv
import logging
import os
import pandas as pd
import pickle
from datetime import datetime
from functools import wraps
from math import cos, asin, sqrt
from typing import List

from data.base_station import BaseStation


def memorize(filename):
    """
    装饰器 保存函数运行结果
    :param filename: 缓存文件位置
    
    Example:
        @memorize('cache/square')
        def square(x):
            return x*x
    
    Todo:
        判断参数是否相同时有坑
    """

    def _memorize(func):
        @wraps(func)
        def memorized_function(*args, **kwargs):
            key = pickle.dumps(args[1:])

            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    cached = pickle.load(f)
                    f.close()
                    if isinstance(cached, dict) and cached.get('key') == key:
                        logging.info(
                            msg='Found cache:{0}, {1} does not have to run'.format(filename, func.__name__))
                        return cached['value']

            value = func(*args, **kwargs)
            with open(filename, 'wb') as f:
                cached = {'key': key, 'value': value}
                pickle.dump(cached, f)
                f.close()
            return value

        return memorized_function

    return _memorize


class DataUtils(object):
    def __init__(self, location_file, user_info_file):
        self.base_stations = self.base_station_reader(location_file)
        self.base_stations = self.user_info_reader(user_info_file)
        self.distances = self.distance_between_stations()

    @memorize('cache/base_stations')
    def base_station_reader(self, path: str):
        """
        读取基站经纬度
        
        :param path: csv文件路径, 基站按地址排序
        :return: List of BaseStations
        """
        bs_data = pd.read_csv(path, header=0, index_col=0)
        base_stations = []
        for index, bs_info in bs_data.iterrows():
            base_stations.append(BaseStation(id=index, addr=bs_info['address'], lat=bs_info['latitude'], lng=bs_info['longitude']))
            logging.debug(msg=f"(Base station:{index}:address={bs_info['address']}, latitude={bs_info['latitude']}, longitude={bs_info['longitude']})")
        return base_stations

    @memorize('cache/base_stations_with_user_info')
    def user_info_reader(self, path: str) -> List[BaseStation]:
        """
        读取用户上网信息
        
        :param path: csv文件路径, 文件应按照基站地址排序
        :return: List of BaseStations with user info
        """
        self.address_to_id = {bs.address: bs.id for bs in self.base_stations}

        req_data = pd.read_csv(path, header=0, index_col=0)
        req_data['start time'] = pd.to_datetime(req_data['start time'])
        req_data['end time'] = pd.to_datetime(req_data['end time'])
        for index, req_info in req_data.iterrows():
            service_time = (req_info['end time'] - req_info['start time']).seconds / 60
            bs_id = self.address_to_id[req_info['address']]
            self.base_stations[bs_id].num_users += 1
            self.base_stations[bs_id].workload += service_time
            logging.debug(msg=f"(User info::address={req_info['address']}, begin_time={req_info['end time']}, end_time={req_info['start time']})")
        return self.base_stations

    @staticmethod
    def _shuffle(l: List):
        random.seed(6767)
        random.shuffle(l)

    @staticmethod
    def calc_distance(lat_a, lng_a, lat_b, lng_b):
        """
        由经纬度计算距离
        
        :param lat_a: 纬度A
        :param lng_a: 经度A
        :param lat_b: 纬度B
        :param lng_b: 经度B
        :return: 距离(km)
        """
        p = 0.017453292519943295  # Pi/180
        a = 0.5 - cos((lat_b - lat_a) * p) / 2 + cos(lat_a * p) * cos(lat_b * p) * (1 - cos((lng_b - lng_a) * p)) / 2
        return 12742 * asin(sqrt(a))  # 2*R*asin...

    @memorize('cache/distances')
    def distance_between_stations(self) -> List[List[float]]:
        """
        计算基站之间的距离
        
        :return: 距离(km)
        """
        assert self.base_stations
        base_stations = self.base_stations
        distances = []
        for i, station_a in enumerate(base_stations):
            distances.append([])
            for j, station_b in enumerate(base_stations):
                dist = DataUtils.calc_distance(station_a.latitude, station_a.longitude, station_b.latitude,
                                               station_b.longitude)
                distances[i].append(dist)
            logging.debug("Calculated distance from {0} to other base stations".format(str(station_a)))
        return distances