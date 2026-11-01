# Task T05 — Nonnegative Weighted Shortest Paths

You are given a directed graph with nonnegative edge weights. Compute the shortest path distance from a source vertex to every other vertex.

## Input
The first line contains three integers: n, m, and src.
Each of the next m lines contains three integers u, v, and w, indicating a directed edge u -> v with weight w.

## Output
Print n integers, one per line, where the i-th line is the shortest distance from src to vertex i, or -1 if vertex i is unreachable.

## Constraints
- 1 <= n <= 200000
- 0 <= m <= 200000
- 0 <= w <= 10^9
- 1 <= src <= n

## Example
Input
```
4 5 1
1 2 2
1 3 5
2 3 1
2 4 3
3 4 1
```

Output
```
0
2
3
5
```

## Notes
All edge weights are nonnegative, so Dijkstra's algorithm is the intended solution. Distances are printed for every vertex from 1 to n, even if the source is not connected to some vertices.
