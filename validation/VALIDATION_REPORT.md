# ConstraintFlip Validation Report

## Summary of the corrected T01 regression

1. T01 exact-sum semantics
   - The correct task is to count contiguous subarrays whose sum is exactly k.
   - For the all-ones case, `5 5 / 1 1 1 1 1` must produce `1`, not `15`.
   - A true no-match regression was added: `5 20 / 1 2 3 4 5` must produce `0`.
   - A one-match regression was added: `6 10 / 1 2 3 4 5 6` must produce `1`.

2. Negative-test C++ generation bug
   - The generated temporary C++ source used a malformed newline escape inside the Python string, which caused the compiler to see a broken character literal.
   - The corrected generation writes the literal source text `cout << 0 << '\n';` as valid C++.
   - The generated file was inspected and the generated source was verified to match the intended content before compilation.

3. Differential-test coverage review
   - The differential-testing suite was reviewed and updated to include T01 explicitly.
   - The oracle remains independent of the reference implementation and uses brute-force counting for the random validation cases.
   - Random seeds are recorded in code, and the task-by-task case counts are printed at the end of the run.

## Preserved semantics

- T06 still uses `UNREACHABLE` instead of any numeric sentinel.
- T01 still uses the positive-only exact-sum task specification.
- No assertions were weakened to force a passing result.

## Current evidence status

The validation state is evidence-based and must be confirmed only by a fresh successful run.
The corrected T01 fixtures are now consistent with the mathematical rule and the independent brute-force oracle.

## Required next step

Run the full validation suite from the project root and preserve the resulting JSON/log evidence before any PASS claim is valid.
