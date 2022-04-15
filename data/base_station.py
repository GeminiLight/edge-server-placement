class BaseStation:
    """基站
    
    Attributes:
        id: 
        address: latitude-longitude
        latitude: 
        longitude: 
        num_users: 
        workload: the total used time (min)
    """

    def __init__(self, id, addr, lat, lng):
        self.id = id
        self.address = addr
        self.latitude = lat
        self.longitude = lng
        self.num_users = 0
        self.workload = 0

    def __str__(self):
        return "No.{0}: {1}".format(self.id, self.address)