# optimal_cdn

Optimal algorithm to allocate client demands in a Content Delivery Network on the minimum possible number of servers of a given capacity, in two stages.

The solution satisfies the following constraints imposed by this telecommunications application:

(i) All client demands are fully satisfied at the end of the second stage of allocation;
(ii) For all clients whose demand is allocated at a given server on a given stage, the proportion of the demand allocated is the same.

Being S the number of servers and N the number of client demands (we suppose S <= N), the algorithm at this stage has a time complexity of O(N*ln(N) + S^2). When completed, its time complexity will drop to O(N ln N) (by replacing a sorted array by a red-black tree).
