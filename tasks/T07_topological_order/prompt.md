# Task T07 — Any Valid Topological Ordering

Given a directed graph, output any valid topological ordering of its vertices.

## Input
The first line contains two integers: n and m.
Each of the next m lines contains two integers u and v, meaning there is a directed edge u -> v.

## Output
Print a valid topological ordering of vertices 1..n as n integers, separated by spaces.
If the graph contains a cycle, print `IMPOSSIBLE`.

## Constraints
- 1 <= n <= 200000
- 0 <= m <= 200000
- The graph may contain duplicate edges.

## Example
Input
```
4 4
1 2
1 3
2 4
3 4
```

Output
```
1 2 3 4
```

Any valid ordering such as `1 3 2 4` would also be acceptable.

## Notes
This task expects Kahn's algorithm. Multiple valid orderings are allowed.
