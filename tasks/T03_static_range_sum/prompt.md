# Task T03 — Static Range Sum

You are given a static array and many range-sum queries. For each query, compute the sum of the elements in the inclusive range [l, r].

## Input
The first line contains two integers: n and m.
The second line contains n integers a1, a2, ..., an.
Each of the next m lines contains two integers l and r.

## Output
For each query, print the sum of a[l] + a[l+1] + ... + a[r].

## Constraints
- 1 <= n, m <= 200000
- -10^9 <= ai <= 10^9
- 1 <= l <= r <= n

## Example
Input
```
5 3
1 2 3 4 5
1 3
2 5
3 3
```

Output
```
6
14
3
```

## Notes
This is the static version of the range-sum problem. The array never changes, so prefix sums are optimal and simple to implement.
