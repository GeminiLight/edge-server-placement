class BaseStation:
    """基站
    
    Attributes:
        id: 编号
        address: 名称 地址
        latitude: 纬度
        longitude: 经度
        user_num: 用户数量
        workload: 总使用时间 单位分钟
    """

    def __init__(self, id, addr, lat, lng):
        self.id = id
        self.address = addr
        self.latitude = lat
        self.longitude = lng
        self.user_num = 0
        self.workload = 0

    def __str__(self):
        return "No.{0}: {1}".format(self.id, self.address)
