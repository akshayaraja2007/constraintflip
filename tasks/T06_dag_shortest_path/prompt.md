# Task T06 — DAG Shortest Paths with Negative Edges

You are given a directed acyclic graph (DAG) with possibly negative edge weights. Compute the shortest path distances from a source vertex to every vertex.

## Input
The first line contains three integers: n, m, and src.
Each of the next m lines contains three integers u, v, and w, indicating a directed edge u -> v with weight w.

## Output
Print n lines.
- If vertex i is reachable from src, print the shortest distance from src to i.
- If vertex i is unreachable, print `UNREACHABLE`.

The value `-2` is not used as a sentinel because a reachable shortest distance can legally be `-2` under the problem constraints.

## Constraints
- 1 <= n <= 200000
- 0 <= m <= 200000
- -10^9 <= w <= 10^9
- 1 <= src <= n
- The graph is guaranteed to be a DAG.

## Example
Input
```
4 4 1
1 2 2
1 3 -1
2 3 3
2 4 -4
```

Output
```
0
2
-1
UNREACHABLE
```

Explanation:
- Distances: d(1)=0, d(2)=2, d(3)=-1, and vertex 4 is unreachable from 1.
- A reachable shortest distance may be negative, including -2, so unreachable vertices must be marked with the literal word `UNREACHABLE`.

## Notes
Because the graph is a DAG and weights may be negative, ordinary Dijkstra is invalid. The intended algorithm is topological sort followed by shortest-path relaxation.
