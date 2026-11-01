# Task T08 — Lexicographically Smallest Topological Ordering

Given a directed graph, output the lexicographically smallest valid topological ordering of its vertices.

## Input
The first line contains two integers: n and m.
Each of the next m lines contains two integers u and v, meaning there is a directed edge u -> v.

## Output
Print the lexicographically smallest topological ordering of vertices 1..n as n integers, separated by spaces.
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

## Notes
This task is a stricter version of T07. The required ordering is not just valid; it must be the smallest lexicographic one among all valid topological sorts.
