import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / 'results' / 'results.json'


def load_results():
    if not RESULTS_PATH.exists():
        print('No results available. Run the grader first.')
        return []
    with RESULTS_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


def summarize(results):
    if not results:
        print('No model experiments exist yet. Results are NOT YET RUN.')
        return

    by_task = {}
    model_pass = {}
    overall = []
    compile_success = 0
    runtime_failures = 0
    correctness_failures = 0

    for entry in results:
        model = entry.get('model', 'unknown')
        model_pass.setdefault(model, 0)
        for task in entry.get('results', []):
            if task.get('status') == 'MISSING_SUBMISSION':
                continue
            score = task.get('score', {}).get('total', 0)
            overall.append(score)
            by_task.setdefault(task['task'], []).append(score)
            model_pass[model] += 1 if task.get('status') == 'ok' else 0
            if task.get('status') == 'COMPILATION_ERROR':
                compile_success += 1
            if task.get('status') == 'ok' and task.get('score', {}).get('total', 0) < 100:
                correctness_failures += 1
            if task.get('details', {}).get('test_results', []) and any(r.get('timed_out') for r in task.get('details', {}).get('test_results', [])):
                runtime_failures += 1

    print('Overall average score:', sum(overall) / len(overall) if overall else 0)
    print('Per-task average score:')
    for task, scores in sorted(by_task.items()):
        print(f'  {task}: {sum(scores) / len(scores) if scores else 0}')
    print('Model pass rate:')
    for model, count in model_pass.items():
        print(f'  {model}: {count / len(results) if results else 0}')
    print('Compilation success rate:', (len(results) - compile_success) / len(results) if results else 0)
    print('Correctness failure rate:', correctness_failures / len(overall) if overall else 0)
    print('Runtime failure rate:', runtime_failures / len(overall) if overall else 0)


if __name__ == '__main__':
    summarize(load_results())
