# ConstraintFlip Benchmark Audit

## Executive summary
This audit reviewed the repository as a benchmark candidate for the micro1 Eval Hackathon.
The repository contains the expected project structure and a reasonable task set, but several correctness issues and validation gaps would invalidate evidence if left unaddressed.

## Critical defects
1. T01 reference implementation was wrong and did not correctly count exact-sum subarrays for positive arrays.
2. The original T01 logic used invalid sliding-window logic that could both undercount and miscount when the target was reached.
3. Several validation and packaging activities were not yet executed on real benchmark data, so the project was not fully reproducible at the time of audit.

## High-priority defects
1. The benchmark harness needed stronger validation of task-side scientific correctness beyond syntax-only checks.
2. The T06 representation needed to clearly distinguish unreachable vertices (`-2`) from valid shortest distances equal to `-1`.
3. T07/T08 validators required explicit correctness checks for duplicate edges, cyclic graphs, and lexicographic ordering edge cases.
4. The benchmark needed a formal audit report to distinguish executed tests from unexecuted code inspection.

## Medium-priority defects
1. The repo initially had some scaffold-only files and no final executed benchmark results.
2. Some of the platform-specific quoting and Windows shell issues made repeated validation difficult unless a direct Python runner was used.
3. The repository had no final benchmark audit narrative or structured risk assessment before this document.

## Fixed issues
- Corrected T01 exact-sum counting logic to use the standard prefix-sum hash-map method, which also generalizes to the signed T02 task.
- Clarified T01/T02 task metadata to ensure the paired scientific contrast is explicit.
- Documented the T06 unreachable sentinel rule (`-2`) as a scientific requirement.
- Strengthened grader-side topological-order validation logic to handle valid alternative outputs for T07 and exact lexicographic checking for T08.
- Added a benchmark audit report to separate executed tests from code inspection.

## Remaining limitations
- No real model submissions were run in this workspace, so no actual model performance evidence is claimed.
- The benchmark is ready for real experimentation, but it is not yet validated with actual model outputs.
- Local execution remains a best-effort harness rather than a hardened sandbox.

## Test counts and actual results
Executed checks during audit:
- Python syntax checks: executed and passed for grader modules and the evaluation harness.
- C++ compile checks: executed for the reference set and the T01 fix was re-checked after correction.
- Task metadata review: executed as code inspection.
- T01 logic review: executed as an independent logical audit.

Important note:
- This audit is not claiming that all hidden tests passed, because no full hidden-data evaluation was run against real model submissions. Hidden contamination risk remains unless benchmark data are fully generated and validated offline.

## Final readiness assessment
Status: conditionally ready for benchmark execution, but not yet ready to claim a complete benchmark result set.
The repository is structurally solid and the scientific task pairings are coherent, but actual model-run validation is still required before making publication claims.
