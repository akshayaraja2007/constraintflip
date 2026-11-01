# Task T02 — Signed Array Subarray Sum

Given an array of integers (possibly negative, zero, or positive) and a target value k, count how many contiguous subarrays have sum exactly k.

## Input
The first line contains two integers: n and k.
The second line contains n integers a1, a2, ..., an.

## Output
Print one integer: the number of subarrays whose sum is exactly k.

## Constraints
- 1 <= n <= 200000
- -10^9 <= ai <= 10^9
- -10^18 <= k <= 10^18

## Example
Input
```
4 0
1 -1 2 -2
```

Output
```
2
```

The valid subarrays are `[1, -1]` and `[2, -2]`.

## Notes
Because values can be negative, a sliding-window approach is not valid. The intended solution uses prefix sums and a hash map that counts previous prefix sums.
