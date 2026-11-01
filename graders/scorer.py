from typing import Dict, Any


COMPILATION_WEIGHT = 10
CORRECTNESS_WEIGHT = 70
RUNTIME_WEIGHT = 20


def score_submission(compilation_result: Dict[str, Any], test_results: list, total_tests: int) -> Dict[str, Any]:
    compilation_points = COMPILATION_WEIGHT if compilation_result.get("ok") else 0

    passed = sum(1 for r in test_results if r.get("correct"))
    correctness_points = 0.0
    if total_tests > 0:
        correctness_points = (passed / total_tests) * CORRECTNESS_WEIGHT

    runtime_points = 0.0
    if all(not r.get("timed_out") and not r.get("runtime_error") for r in test_results):
        runtime_points = RUNTIME_WEIGHT

    total = compilation_points + correctness_points + runtime_points
    return {
        "compilation": compilation_points,
        "correctness": correctness_points,
        "runtime": runtime_points,
        "total": total,
        "passed_tests": passed,
        "total_tests": total_tests,
    }
