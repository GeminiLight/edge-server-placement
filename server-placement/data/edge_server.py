class EdgeServer(object):
    
    def __init__(self, id, latitude, longitude, base_station_id=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.base_station_id = base_station_id
        self.assigned_base_stations = []
        self.workload = 0