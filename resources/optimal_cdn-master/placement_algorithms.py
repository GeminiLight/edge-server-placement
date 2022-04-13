import heapq
import copy

from placement import PlacementManager


def placement(clients, servers):
    """
    Greedy algorithm.
    Sort clients in descending order of their demand.
    For each client, place it into the server that has the lowest used_capacity.
    """
    placement_manager = PlacementManager(servers)
    clients.sort(reverse=True)
    for client in clients:
        server = heapq.heappop(servers)
        placement_manager.place_client(client, server)
        heapq.heappush(servers, server)
    return placement_manager


def optimal_placement(clients, servers):
    """
    Uses the placement algorithm to get an allocation of clients in the desired number of servers with used capacities all close to one another.
    Uses this allocation to place the clients in the servers in such a way to satisfy all the constraints with the minimal possible used capacity for each server, in two time steps for each server.
    """
    placement_manager = placement(clients, servers)
    avg_used_capacity = sum(server.used_capacity for server in placement_manager.servers) / len(placement_manager.servers)
    sorted_servers = sorted(placement_manager.servers)
    max_used_capacity = sorted_servers[-1].used_capacity
    index, next_server = __find_closest_used_capacity(sorted_servers, avg_used_capacity, True)
    del sorted_servers[index]
    accumulated_capacity = avg_used_capacity + next_server.used_capacity - max_used_capacity
    lambda1 = accumulated_capacity / next_server.used_capacity
    lambda2 = 1.0 - lambda1
    next_clients = placement_manager.get_clients_served_by(next_server).keys()
    first_clients = copy.copy(list(next_clients))
    placement_manager.change_multiplicative_factor(next_server, lambda1)
    next_server.used_capacity = lambda1*sum(client.demand for client in first_clients)
    last_server = next_server
    for count in range(1, len(placement_manager.servers)):
        target = (count+2)*avg_used_capacity - max_used_capacity - accumulated_capacity
        index, next_server = __find_closest_used_capacity(sorted_servers, target, accumulated_capacity < (count+1)*avg_used_capacity - max_used_capacity)
        del sorted_servers[index]
        next_clients = placement_manager.get_clients_served_by(next_server).keys()
        accumulated_capacity += next_server.used_capacity
        lambda1 = (accumulated_capacity - count*avg_used_capacity) / next_server.used_capacity
        placement_manager.change_multiplicative_factor(next_server, lambda1)
        next_server.used_capacity = lambda1*sum(client.demand for client in next_clients)
        placement_manager.set_multiplicative_factor(last_server, next_clients, 1.0 - lambda1)
        last_server.used_capacity += (1.0 - lambda1)*sum(client.demand for client in next_clients)
        last_server = next_server
    placement_manager.set_multiplicative_factor(last_server, first_clients, lambda2)
    last_server.used_capacity += lambda2*sum(client.demand for client in first_clients)
    return placement_manager


def __find_closest_used_capacity(servers, target, bigger):
    """
    Given a sorted list of servers, finds the server in that list whose used capacity is the smallest amongst those bigger
    than a given target (or biggest amongst those smaller than the target).
    Returns this server and its position on the list.
    """
    if len(servers) == 1:
        return [0, servers[0]]
    if target > servers[-1].used_capacity:
        return [len(servers)-1, servers[-1]]
    len_med = int(len(servers)/2)
    closest = [len_med, servers[len_med]]
    if servers[len_med].used_capacity == target:
        return closest
    if servers[len_med].used_capacity > target:
        temp = __find_closest_used_capacity(servers[:len_med], target, bigger)
        if bigger:
            if temp[1].used_capacity >= target:
                return temp
            return closest
        return temp
    temp = __find_closest_used_capacity(servers[len_med+1:], target, bigger)
    temp[0] += len_med + 1
    if bigger:
        return temp
    if temp[1].used_capacity <= target:
        return temp
    return closest
    
