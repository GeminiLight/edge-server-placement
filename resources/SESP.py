import math
import numpy as np

M = 7030
N = 700
# M = 300
# N = 30
stepnum = M // N

mission_num = [np.random.randint(100, 1000) for i in range(M)]        # 随机生成每个基站接收到的数据包的数量
lamuda = []                    # 每个基站收到的数据包的大小总和
lamuda_list_current = []       # 存储删除异常数据包后正常的数据包
lamuda_list_origin = []        # 存储未删除异常数据包 的数据包
error_num = [0 for i in range(M)]       # 存储每个基站中错误的数据包的数量

# 区分安全和非安全任务
for i in range(M):
    a = []
    a = [np.random.randint(400, 601) for i in range(mission_num[i])]  # 400-600Kb随机值
    lamuda_list_origin.append(a)            # 将a加入未删除元素时的任务总列表
    s = np.random.randint(100, 1000)        # 密钥，用于模拟不安全的任务
    for x in a:
        f = np.random.randint(100, 1000)    # 辅助变量
        y = (x + f) % 1000
        if y == s:
            a.remove(x)
            error_num[i] += 1
    lamuda.append(sum(a))
    lamuda_list_current.append(a)
# print(lamuda_list)
print('任务总数' + str(sum(mission_num)))
print('不安全任务总数' + str(sum(error_num)))

correct_lamuda = [sum(x) / 100 for x in lamuda_list_origin]         # 每个基站用于验证的数据包的大小
# print(correct_lamuda)


miu = [x * 2 for x in lamuda]  # lambda * 2(数值上) 兆周   单位(兆周)
correct_miu = [x * 2 for x in correct_lamuda]         # 用于验证的数据包处理需要的CPU周期数
ve = 3000  # 3Mbps
vc = 1000  # 1Mbps
re = 2000  # 2GHz    单位(兆周)
rc = 4000  # 4GHz    单位(兆周)
kmax = 16
cimax = 26
R = 1.5

e = [[] for i in range(N)]  # server覆盖的基站集合初始化
# print(len(e[0]))
k = [0 for i in range(N)]  # e的长度
u = [0 for i in range(N)]  # 效用函数
# A = [[0] * M for i in range(N)]
movenum = [0 for i in range(N)]

toldelay_correct = 0
workload = [0 for i in range(N)]
toldelay_covered = 0    # 覆盖的基站的延迟
toldelay_edge = 0       # 占用的基站的延迟
toldelay_cloud = 0      # 未覆盖的基站的延迟
proe = [x / re for x in miu]
proc = [x / rc for x in miu]
trc = [x / vc for x in lamuda]


def distance(lon1, lat1, lon2, lat2):  # 经度1，纬度1， 精度2，纬度2
    R = 6373.0
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    d = 2 * math.asin(math.sqrt(a)) * R
    return d  # distance


def dist(x1, x2):  # x1 x2 为两个基站的经纬度坐标，求x1与x2的距离
    d = distance(math.radians(float(x1[0])), math.radians(float(x1[1])),
                 math.radians(float(x2[0])), math.radians(float(x2[1])))
    return d  # dist


f = open('E:\上海.txt', 'r')  # 打开文件
location = []
for line in f:
    line = line.rstrip().split(',')
    location.append(tuple(line))
f.close()
# print(location)                           #打开文件

# print(len(location))                       #测试基站数组的个数

server_location = [x for x in location if location.index(x) % stepnum == 0]  # server初始位置
# print(server_location)                       #测试服务器数组
# print(len(server_location))                  #测试服务器数组的个数
premigrate = [[] for i in range(N)]  # 初始化预迁移列表
location2 = location.copy()

'''
location1 = location.copy()
for x in server_location:                           #初始边缘服务器覆盖的基站集合
    print(server_location.index(x))
    for y in location1:
        if y != x and dist(x, y) <= R:
            if len(e[server_location.index(x)]) < kmax:
                A[server_location.index(x)][location1.index(y)] = 1
                e[server_location.index(x)].append(y)
                location1.remove(y)
            else:
                break
print(len(location))
'''

'''
file = open('E:\用列表e写入覆盖数目.txt', 'w')  #将初始server覆盖的基站数目写入文件
for i in range(len(server_location)):
    k.append(len(e[i]))                     #初始k
    file.write(str(i+1) + ':' + str(len(e[i])) + '\n')
file.close()                                #将初始server覆盖的基站数目写入文件
'''


result = open("E:\结果N = 700.txt", 'w')
result.write('任务总数' + str(sum(mission_num)) + '\n')
result.write('不安全任务总数' + str(sum(error_num)) + '\n')
for j in range(N):  # 迁移各个点
    # if j == 0:  # 测试语句
    #     break
    print('当前正在进行迁移的服务器为：' + str(j))
    budong = 0
    x = server_location[j]
    print(x)
    print(location.index(x))
    if x not in location2:
        x = location2[0]  # 如果当前边缘服务器位置被覆盖，则指定其为location2中的第一个位置

    num = 0
    e[j] = []
    for y in location2:  # 计算初始效用函数及覆盖的基站数目
        if y != x and dist(x, y) <= R:
            num += 1
            u[j] += lamuda[location.index(y)] / ve
    k[j] = num
    u[j] += proe[j]
    if k[j] < kmax:
        while True:
            mindist = min([dist(y, x)  # 不能迁移到已经预迁移过的点 不能迁移到其他边缘服务器占用的点
                           for y in location2 if y not in server_location
                           and y not in premigrate[j]])  # 找与当前边缘服务器距离最近的点
            # print("最近距离：", end='')
            # print(mindist)  # 与当前服务器位置的最近距离
            miny = [y for y in location2 if dist(y, x) == mindist
                    and y not in server_location]  # miny[0]是与当前服务器位置最近距离的点
            # print("距离最近的点：", end='')
            # print(miny[0])
            # print(location.index(miny[0]))
            premigrate[j].append(miny[0])
            new_server = miny[0]
            new_num = 0
            new_u = 0
            for y in location2:
                if y != new_server and dist(y, new_server) <= R:
                    new_num += 1
                    new_u += lamuda[location.index(y)] / ve
            print('当前最新的点覆盖的基站数目：', end='')
            k[j] = new_num
            print(k[j])

            new_u += proe[j]
            if new_u > u[j]:
                x = new_server  # 新服务器位置
                u[j] = new_u
                # print(premigrate[2])     #显示当找到本轮可迁移到的点时 之前已经预迁移的点数量
                budong = 0
            else:
                budong += 1
                movenum[j] += 1
            print('当前不动的次数：' + str(budong))
            if budong > cimax:
                break
    i = 0  # 计数变量
    for y in location2:
        if dist(y, x) <= R and i < kmax and y != x:
            e[j].append(y)
            workload[j] += miu[location.index(y)]
            location2.remove(y)
            i += 1
    toldelay_covered += u[j]
    workload[j] += miu[location.index(x)]
    location2.remove(x)
    print('第' + str(j) + '个边缘服务器覆盖的基站数目：' + str(k[j]))
    print('第' + str(j) + '个边缘服务器坐标为：')
    print(x)
    print('第' + str(j) + '个边缘服务器位置为：')
    print('第' + str(j) + '个边缘服务器总移动次数为：' + str(movenum[j]))
    print(location.index(x))
    result.write('第' + str(j) + '个边缘服务器覆盖的基站数目：' + str(k[j]) + '\n')
    result.write('第' + str(j) + '个边缘服务器坐标为：' + str(x) + '\n')
    result.write('第' + str(j) + '个边缘服务器位置为：' + str(location.index(x)) + '\n')
    result.write('第' + str(j) + '个边缘服务器总移动次数为：' + str(movenum[j]) + '\n')
    result.write('\n')
    print('边缘服务器' + str(j) + '的负载为：' + str(workload[j]) + ' Megacycles')

tol = sum(k)
print('总覆盖基站数为：' + str(tol + N))
result.write('总覆盖基站数为：' + str(tol + N) + '\n')
result.write('被覆盖的基站的总延迟(边缘服务器的效用函数总和)为：' + str(toldelay_covered) + 's\n')
for x in server_location:
    toldelay_edge += proe[location.index(x)]  # 占据的基站延迟
for i in range(M):
    if location[i] in location2:
        toldelay_cloud += proc[i] + trc[i]  # 未被覆盖的基站延迟
        toldelay_correct += 2 * correct_lamuda[i] / vc
        toldelay_correct += correct_miu[i] / rc
    else:
        toldelay_correct += 2 * correct_lamuda[i] / ve
        toldelay_correct += correct_miu[i] / re

result.write('被覆盖充当边缘服务器的基站的总延迟为：' + str(toldelay_edge) + 's\n')
result.write('未被覆盖的基站的总延迟(传输到云端)为：' + str(toldelay_cloud) + 's\n')
toldelay = toldelay_cloud + toldelay_covered + toldelay_edge + toldelay_correct
result.write('场景的总延迟为：' + str(toldelay) + 's\n')
result.write('场景的平均延迟为：' + str(toldelay / M) + 's\n')
print('场景的总延迟为：' + str(toldelay) + 's')
print('场景的平均延迟为：' + str(toldelay / M) + 's')
result.write('边缘服务器的平均延迟为：' + str((toldelay_covered + toldelay_edge + toldelay_correct) / N) + 's\n')
print('边缘服务器的平均延迟为：' + str((toldelay_covered + toldelay_edge + toldelay_correct) / N) + 's')
print('场景的总的移动次数为：' + str(sum(movenum)))
print('场景的平均移动次数为：' + str(sum(movenum) / N))
result.write('场景的总的移动次数为：' + str(sum(movenum)) + '\n')
result.write('场景的平均移动次数为：' + str(sum(movenum) / N) + '\n')
ave_workload = sum(workload) / N
print('边缘服务器的总负载为：' + str(sum(workload)/100000) + ' *10^5 Megacycles')
result.write('边缘服务器的总负载为：' + str(sum(workload)/100000) + ' *10^5 Megacycles' + '\n')
print('边缘服务器的平均负载为：' + str(ave_workload/100000) + ' *10^5 Megacycles')
result.write('边缘服务器的平均负载为：' + str(ave_workload/100000) + ' *10^5 Megacycles' + '\n')
print('用于验证安全性的数据包传送和处理的总延迟为：' + str(toldelay_correct) + 's')
result.write('用于验证安全性的数据包传送和处理的总延迟为：' + str(toldelay_correct) + 's\n')
print('用于验证安全性的数据包传送和处理的基站平均延迟为：' + str(toldelay_correct / M) + 's')
result.write('用于验证安全性的数据包传送和处理的基站平均延迟为：' + str(toldelay_correct / M) + 's\n')
result.close()

'''
fi = open('E:\矩阵.txt', 'w')             #测试矩阵A是否赋值成功
for i in range(N):
    s = 0
    for j in range(M):
        s += A[i][j]
    fi.write(str(i+1) + ':' + str(s) + '\n')
fi.close()                                  #测试矩阵A是否赋值成功
'''

'''
file = open('E:\备注.txt', 'w')           #将server覆盖的基站个数写入文件
for y in server_location:
    num = 0
    for x in location:
        if x != y:
            d = dist(x, y)
            if d <= R:
                num += 1
    print(location.index(y)+1, end = '：')
    print(num)
    file.write(str(location.index(y)+1) + ':' + str(num) + '\n')
file.close()                              #将server覆盖的基站个数写入文件
'''
