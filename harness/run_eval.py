import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from graders.compiler import compile_cpp
from graders.correctness import check_task_output
from graders.performance import run_program
from graders.scorer import score_submission

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
REFERENCE_DIR = ROOT / "reference"
RESULTS_DIR = ROOT / "results"
SUBMISSIONS_DIR = ROOT / "submissions"


def task_dirs():
    return sorted([p for p in TASKS_DIR.iterdir() if p.is_dir() and p.name.startswith("T")])


def load_task(task_dir: Path) -> Dict[str, Any]:
    with (task_dir / "task.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def compile_reference(task: Dict[str, Any], task_dir: Path) -> Dict[str, Any]:
    ref_src = REFERENCE_DIR / f"{task['id']}.cpp"
    ref_bin = task_dir / "reference_exec"
    if not ref_src.exists():
        return {"ok": False, "error": "REFERENCE_SOURCE_MISSING", "stderr": "Missing reference source"}
    return compile_cpp(str(ref_src), str(ref_bin), timeout_seconds=30)


def compile_candidate(source_path: Path, task_id: str, model_name: str, trial: int) -> Dict[str, Any]:
    build_dir = ROOT / "submissions" / model_name / f"{task_id}_trial_{trial}_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    exe_path = build_dir / "candidate"
    result = compile_cpp(str(source_path), str(exe_path), timeout_seconds=20)
    result["build_dir"] = str(build_dir)
    return result


def list_task_tests(task_dir: Path) -> List[Path]:
    tests_dir = task_dir / "tests"
    if not tests_dir.exists():
        return []
    return sorted(p for p in tests_dir.iterdir() if p.suffix == ".in")


def read_cases(task_dir: Path) -> List[Dict[str, Any]]:
    cases = []
    for input_path in list_task_tests(task_dir):
        out_path = input_path.with_suffix(".out")
        if not out_path.exists():
            continue
        cases.append({
            "input_path": input_path,
            "output_path": out_path,
            "input_text": input_path.read_text(encoding="utf-8"),
            "expected_text": out_path.read_text(encoding="utf-8"),
        })
    return cases


def execute_reference(ref_binary: str, input_text: str) -> Dict[str, Any]:
    return run_program(ref_binary, input_text, timeout_seconds=10)


def run_task_validation() -> Dict[str, Any]:
    results = []
    for task_dir in task_dirs():
        task = load_task(task_dir)
        ref_bin = task_dir / "reference_exec"
        if not ref_bin.exists():
            compile_result = compile_reference(task, task_dir)
            if not compile_result["ok"]:
                results.append({"task": task["id"], "status": "compile_failed", "details": compile_result})
                continue
            ref_bin = compile_result["output_path"]
        for case in read_cases(task_dir):
            res = execute_reference(str(ref_bin), case["input_text"])
            if res["timed_out"]:
                results.append({"task": task['id'], "status": "timeout", "case": case['input_path'].name, "details": res})
                continue
            actual = res["stdout"]
            validation = check_task_output(task['id'], case['input_text'], case['expected_text'], actual)
            if not validation["correct"]:
                results.append({
                    "task": task['id'],
                    "status": "reference_mismatch",
                    "case": case['input_path'].name,
                    "expected": case['expected_text'],
                    "actual": actual,
                })
                continue
        results.append({"task": task['id'], "status": "ok"})
    return {"tasks": results}


def grade_model(model_name: str, trial: int) -> Dict[str, Any]:
    model_results = []
    for task_dir in task_dirs():
        task = load_task(task_dir)
        submission_candidates = list((SUBMISSIONS_DIR / model_name).glob(f"{task['id']}_trial_{trial}.cpp"))
        if not submission_candidates:
            model_results.append({
                "task": task['id'],
                "status": "MISSING_SUBMISSION",
                "score": 0,
                "details": {"model": model_name, "trial": trial},
            })
            continue
        source_path = submission_candidates[0]
        compile_result = compile_candidate(source_path, task['id'], model_name, trial)
        if not compile_result["ok"]:
            model_results.append({
                "task": task['id'],
                "status": "COMPILATION_ERROR",
                "score": 0,
                "details": compile_result,
            })
            continue
        exe_path = compile_result["output_path"]
        test_cases = read_cases(task_dir)
        test_results = []
        for case in test_cases:
            completed = run_program(exe_path, case["input_text"], timeout_seconds=2.0)
            if completed["timed_out"]:
                test_results.append({"case": case['input_path'].name, "correct": False, "timed_out": True, "runtime_error": False})
                continue
            if completed["runtime_error"]:
                test_results.append({"case": case['input_path'].name, "correct": False, "timed_out": False, "runtime_error": True})
                continue
            validation = check_task_output(task['id'], case['input_text'], case['expected_text'], completed['stdout'])
            test_results.append({
                "case": case['input_path'].name,
                "correct": validation['correct'],
                "timed_out": False,
                "runtime_error": False,
                "validator_used": validation.get('validator_used'),
            })
        score = score_submission(compile_result, test_results, len(test_cases))
        model_results.append({
            "task": task['id'],
            "status": "ok",
            "score": score,
            "details": {"tests_run": len(test_cases), "test_results": test_results},
        })
    return {"model": model_name, "trial": trial, "results": model_results}


def export_results_json(results: List[Dict[str, Any]], path: Path):
    with path.open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


def export_summary_csv(results: List[Dict[str, Any]], path: Path):
    rows = []
    for item in results:
        if not isinstance(item, dict) or 'model' not in item:
            continue
        for task in item.get('results', []):
            rows.append({
                'model': item['model'],
                'trial': item['trial'],
                'task': task['task'],
                'status': task['status'],
                'score': task.get('score', {}).get('total', 0),
                'passed_tests': task.get('score', {}).get('passed_tests', 0),
                'total_tests': task.get('score', {}).get('total_tests', 0),
            })
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['model', 'trial', 'task', 'status', 'score', 'passed_tests', 'total_tests'])
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description='ConstraintFlip evaluation harness')
    parser.add_argument('--validate-references', action='store_true', help='Compile and validate reference outputs.')
    parser.add_argument('--grade', action='store_true', help='Grade a candidate model submission.')
    parser.add_argument('--model', type=str, default='Model_A')
    parser.add_argument('--trial', type=int, default=1)
    args = parser.parse_args()

    if args.validate_references:
        validation = run_task_validation()
        print(json.dumps(validation, indent=2))
        return

    if args.grade:
        result = grade_model(args.model, args.trial)
        RESULTS_DIR.mkdir(exist_ok=True)
        export_results_json(result['results'], RESULTS_DIR / 'results.json')
        export_summary_csv([result], RESULTS_DIR / 'summary.csv')
        print(json.dumps(result, indent=2))
        return

    print('No action specified. Use --validate-references or --grade.')


if __name__ == '__main__':
    main()
