# Task T01 — Positive Array Subarray Sum

Given an array of strictly positive integers and a target value k, count how many contiguous subarrays have sum exactly k.

## Input
The first line contains two integers: n and k.
The second line contains n integers a1, a2, ..., an.

## Output
Print one integer: the number of subarrays whose sum is exactly k.

## Constraints
- 1 <= n <= 200000
- 1 <= ai <= 10^9
- 1 <= k <= 10^18

## Example
Input
```
5 3
1 2 3 1 1
```

Output
```
2
```

The valid subarrays are `[1,2]` and `[3]`.

## Notes
This benchmark expects the sliding-window technique because all values are positive. A model that naively reuses a generic prefix-sum strategy is not the intended optimization for this constraint regime.
