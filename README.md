# ConstraintFlip

Constraint-Aware Algorithm Selection Benchmark for AI Coding Models.

## Project overview
ConstraintFlip is a C++17 benchmark for evaluating whether AI coding models adapt their algorithm when a small change in task constraints invalidates a previously suitable approach. The benchmark focuses on algorithm selection, constraint sensitivity, and correctness under realistic competitive-programming conditions.

## Research hypothesis
AI coding models can often produce correct solutions for familiar problems, but they may fail to adapt when the input constraints change in a way that fundamentally alters the required algorithm. This benchmark is designed to isolate precisely those transitions.

## Real-world relevance
Modern coding assistants are commonly used for algorithmic work, but many failures come from hidden assumptions about constraints rather than from a lack of raw ability. This benchmark measures whether a model notices when the problem changes from a positive-only sequence to a signed sequence, or from static queries to dynamic updates.

## Domain and expertise
The benchmark is aimed at algorithmic problem solving, data structures, graph theory, and evaluation methodology in AI model benchmarking.

## Why these tasks matter
The eight tasks progressively vary the task conditions while preserving the broad competitive-programming flavor. The most informative pairs are:
- T01 vs T02: positive-only sum vs signed sum
- T03 vs T04: static vs dynamic range sums
- T05 vs T06: nonnegative weights vs negative DAG weights
- T07 vs T08: any valid order vs lexicographically smallest order

These pairs are designed to reveal whether a model chooses a general-purpose solution without recognizing the constraint-driven algorithmic shift.

## Task descriptions
- T01: Positive Array Subarray Sum — count subarrays of exact sum k under positive-only values using sliding window.
- T02: Signed Array Subarray Sum — same goal with possibly negative values, requiring prefix sums and a hash map.
- T03: Static Range Sum — multiple range queries over a fixed array using prefix sums.
- T04: Dynamic Range Sum — point updates plus range sums using a Fenwick tree or segment tree.
- T05: Nonnegative Weighted Shortest Paths — shortest paths with nonnegative edges using Dijkstra.
- T06: DAG Shortest Paths with Negative Edges — shortest paths in a DAG with negative values using topological order relaxation.
- T07: Any Valid Topological Ordering — output any valid order or IMPOSSIBLE.
- T08: Lexicographically Smallest Topological Ordering — output the smallest valid order, requiring a min-heap.

## Architecture
- `tasks/`: task definitions, prompts, examples, and hidden test inputs
- `reference/`: C++17 reference solutions
- `graders/`: Python modules for compilation, correctness, performance, and scoring
- `harness/`: command-line evaluation workflow
- `results/`: JSON and CSV outputs
- `submissions/`: model submission files
- `transcripts/`: archived model prompts and responses

## Installation
1. Install a C++17 compiler, such as GCC or MinGW-w64.
2. Install Python 3.9+.
3. Create a virtual environment if desired.
4. Install project dependencies from `requirements.txt`.

Example:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Compiler requirements
The local harness expects a C++ compiler available on PATH. Common options:
- Windows: MinGW-w64 (`g++`)
- Linux: `g++`
- macOS: `clang++`

## Execution commands
Reference validation:
```
python harness/run_eval.py --validate-references
```

Model grading:
```
python harness/run_eval.py --grade --model "Model A" --trial 1
```

Collect results:
```
python harness/collect_results.py
```

## Scoring methodology
Each task is scored as follows:
- Compilation: 10 points
- Functional correctness: 70 points
- Runtime: 20 points

Correctness points are allocated proportionally to passed tests. Runtime points are awarded only when all tests run within their configured time budgets. The scoring components remain separate in the result records.

## Reference solution validation
Reference solutions are compiled and checked against their task test suites. For suitable problems, brute-force and differential checks are used where a simpler oracle is available. Important scientific safeguards include:
- T06 distinguishes unreachable vertices from reachable vertices with shortest distance -1 using the sentinel -2.
- Topological-order tasks accept any valid ordering for T07 and require lexicographic exactness for T08.
- All reference programs are checked for correctness before being trusted for grading.

## Model experiment protocol
1. Save the raw model prompt and final answer in the `transcripts/` directory.
2. Extract the candidate C++ code.
3. Place the source in `submissions/<Model>/<Task>_trial_<N>.cpp`.
4. Run the grader.
5. Record the scoring output and any failure categories.
6. Archive the raw model response alongside the extracted source.

## Results table template
```
Model | Trial | Task | Compile | Correctness | Runtime | Total | Notes
```

## Failure analysis
The benchmark records separate failure categories for:
- compilation errors
- wrong answers
- runtime errors
- timeouts
- missing submissions
- reference validation issues

These failures are not collapsed into a single score value so that it remains possible to analyze why a model failed.

## Reproducibility
All experiments should be reproducible by explicitly recording:
- model name/version
- task ID
- trial number
- date and time
- prompt text
- source file used
- compiler version
- execution environment
- result files

## Runtime and cost reporting
This project does not require paid APIs or model access. Local evaluation is run entirely on the host machine. Runtime is measured per test case, and cost is effectively limited to local compute time.

## Limitations
- This is a local benchmark, not a secure sandbox.
- Candidate programs are treated as untrusted code.
- The project intentionally does not claim memory isolation beyond local best-effort execution.
- The benchmark measures algorithmic adaptation in a structured but limited set of tasks.

## Provenance and prior work
This benchmark is an original local evaluation project designed for the micro1 Eval Hackathon. It is inspired by constraint-sensitive algorithm assessment in competitive programming and AI coding evaluations.

## AI-use disclosure
This project was implemented with the assistance of an AI coding system, but the benchmark design, validation, and final documentation were reviewed for correctness and scientific integrity.

## Human review checklist
- Every task has a valid prompt and example.
- Every reference solution compiles and passes tests.
- Output formatting matches the specification.
- T06 and topological-order validators distinguish unreachable or valid alternatives correctly.
- Results are archived without fabrication.

## Not yet run
The benchmark is ready to run, but no actual model experiments are recorded yet. Any results in `results/` are generated from local validation, not from real model submissions.

## Final ZIP packaging
A packaging command is provided in `package_submission.py`.

## Example of result structure
```
results/
  results.json
  summary.csv
```
