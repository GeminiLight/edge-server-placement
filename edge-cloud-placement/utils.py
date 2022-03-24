import random
import csv
import logging
import os
import pickle
from datetime import datetime
from functools import wraps
from math import cos, asin, sqrt
from typing import List

from base_station import BaseStation


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
        self.base_station_locations = self.base_station_reader(location_file)
        self.base_stations = self.user_info_reader(user_info_file)
        self.distances = self.distance_between_stations()

    @memorize('cache/base_stations')
    def base_station_reader(self, path: str) -> [BaseStation]:
        """
        读取基站经纬度
        
        :param path: csv文件路径, 基站按地址排序
        :return: List of BaseStations
        """
        with open(path, 'r', ) as f:
            reader = csv.reader(f)
            base_stations = []
            count = 0
            for row in reader:
                address = row[0]
                latitude = float(row[1])
                longitude = float(row[2])
                base_stations.append(BaseStation(id=count, addr=address, lat=latitude, lng=longitude))
                logging.debug(
                    msg="(Base station:{0}:address={1}, latitude={2}, longitude={3})".format(count, address, latitude,
                                                                                             longitude))
                count += 1
            f.close()
            return base_stations

    @memorize('cache/base_stations_with_user_info')
    def user_info_reader(self, path: str) -> List[BaseStation]:
        """
        读取用户上网信息
        
        :param path: csv文件路径, 文件应按照基站地址排序
        :return: List of BaseStations with user info
        """
        assert self.base_station_locations
        with open(path, 'r') as f:
            reader = csv.reader(f)
            bs = self.base_station_locations
            base_stations = []
            count = 0
            last_index = 0
            last_station = None  # type: BaseStation
            next(reader)  # 跳过标题
            for row in reader:
                address = row[4]
                s_begin_time = row[2]
                s_end_time = row[3]
                logging.debug(
                    msg="(User info::address={0}, begin_time={1}, end_time={2})".format(address, s_begin_time,
                                                                                        s_end_time))

                # 计算使用时间
                try:
                    begin_time = datetime.strptime(s_begin_time, r"%Y/%m/%d %H:%M")
                    end_time = datetime.strptime(s_end_time, r"%Y/%m/%d %H:%M")
                    minutes = (begin_time - end_time).seconds / 60
                except ValueError as ve:
                    logging.warning("Failed to convert time: " + str(ve))
                    minutes = 0

                if (not last_station) or (not address == last_station.address):
                    last_station = None
                    for i, item in enumerate(bs[last_index:]):
                        if address == item.address:
                            last_index = i
                            last_station = item
                            last_station.id = count
                            count += 1
                            base_stations.append(last_station)
                            break
                if last_station:
                    last_station.user_num += 1
                    last_station.workload += minutes
            f.close()
            DataUtils._shuffle(base_stations)
            for i, item in enumerate(base_stations):
                item.id = i
            return base_stations

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
