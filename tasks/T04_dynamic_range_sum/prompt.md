# Task T04 — Dynamic Range Sum

You are given an array of integers. The array may be updated by assigning a single position to a new value, and you need to answer range-sum queries over the current array.

## Input
The first line contains two integers: n and m.
The second line contains n integers a1, a2, ..., an.
Each of the next m lines contains either:
- `U x v`, meaning set a[x] = v
- `Q l r`, meaning output the sum of a[l] + a[l+1] + ... + a[r]

## Output
For each query of type `Q`, print the sum of the inclusive range [l, r].

## Constraints
- 1 <= n, m <= 200000
- -10^9 <= ai, v <= 10^9
- 1 <= x, l, r <= n
- l <= r for every query of type `Q`

## Example
Input
```
5 5
1 2 3 4 5
Q 1 5
U 3 10
Q 2 4
Q 1 5
U 5 1
Q 3 5
```

Output
```
15
17
23
10
```

## Notes
Because the array changes over time, prefix sums are no longer sufficient. A Fenwick tree or segment tree is the intended data structure for efficient dynamic range-sum queries.
