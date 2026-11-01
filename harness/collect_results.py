import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / 'results'


def collect_model_results():
    summaries = []
    for model_dir in sorted((ROOT / 'submissions').iterdir()):
        if not model_dir.is_dir():
            continue
        for results_file in sorted(model_dir.glob('*.json')):
            try:
                with results_file.open('r', encoding='utf-8') as f:
                    summaries.extend(json.load(f))
            except Exception:
                continue
    return summaries


def main():
    results = collect_model_results()
    RESULTS_DIR.mkdir(exist_ok=True)
    with (RESULTS_DIR / 'results.json').open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    with (RESULTS_DIR / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['model', 'trial', 'task', 'status', 'score', 'passed_tests', 'total_tests'])
        for entry in results:
            model = entry.get('model', '')
            trial = entry.get('trial', '')
            for task in entry.get('results', []):
                writer.writerow([
                    model,
                    trial,
                    task.get('task', ''),
                    task.get('status', ''),
                    task.get('score', {}).get('total', 0),
                    task.get('score', {}).get('passed_tests', 0),
                    task.get('score', {}).get('total_tests', 0),
                ])
    print(f'Collected {len(results)} result entries into {RESULTS_DIR}')


if __name__ == '__main__':
    main()
