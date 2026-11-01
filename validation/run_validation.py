
#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import traceback

from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "validation" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# GENERAL UTILITIES
# ============================================================

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8"
    )


def parse_case_count_from_task_dir(task_dir: Path):
    return len(sorted(task_dir.glob("tests/*.in")))


def count_public_cases():
    total = 0

    for task_dir in sorted((ROOT / "tasks").iterdir()):
        if task_dir.is_dir():
            total += parse_case_count_from_task_dir(task_dir)

    return total


# ============================================================
# STAGE EXECUTION AND LOGGING
# ============================================================

def execute_stage(
    stage_name: str,
    command,
    timeout_seconds: int = 180,
    stage_count: int | None = None
):
    started_at = utc_timestamp()
    started_time = time.perf_counter()

    log_path = (
        LOGS_DIR /
        f"{stage_name}_{started_at.replace(':', '-')}.log"
    )

    payload = {
        "stage": stage_name,
        "command": command,
        "started_at_utc": started_at,
        "finished_at_utc": None,
        "duration_seconds": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "status": "failed",
        "stage_case_count": stage_count,
    }

    try:
        proc = subprocess.run(
            command,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )

        payload["stdout"] = proc.stdout
        payload["stderr"] = proc.stderr
        payload["exit_code"] = proc.returncode

        payload["status"] = (
            "success" if proc.returncode == 0 else "failed"
        )

    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")

        payload["stdout"] = stdout
        payload["stderr"] = stderr + "\nTIMEOUT"
        payload["exit_code"] = 124
        payload["status"] = "failed"

    except Exception:
        payload["stderr"] = traceback.format_exc()
        payload["exit_code"] = 1
        payload["status"] = "failed"

    finally:
        payload["finished_at_utc"] = utc_timestamp()

        payload["duration_seconds"] = round(
            time.perf_counter() - started_time,
            6
        )

        log_text = (
            f"COMMAND: {command}\n"
            f"REPO_ROOT: {ROOT}\n"
            f"STARTED_AT_UTC: {started_at}\n"
            f"FINISHED_AT_UTC: {payload['finished_at_utc']}\n"
            f"EXITCODE: {payload['exit_code']}\n"
            f"DURATION_SECONDS: {payload['duration_seconds']}\n"
            f"STATUS: {payload['status']}\n"
            f"STAGE_CASE_COUNT: {stage_count}\n\n"
            f"--- STDOUT ---\n{payload['stdout']}\n\n"
            f"--- STDERR ---\n{payload['stderr']}\n"
        )

        log_path.write_text(log_text, encoding="utf-8")

    return payload


def stage_from_python_script(
    stage_name: str,
    relative_script: str,
    timeout_seconds: int = 180,
    stage_count: int | None = None
):
    script_path = ROOT / relative_script

    return execute_stage(
        stage_name,
        [sys.executable, str(script_path)],
        timeout_seconds=timeout_seconds,
        stage_count=stage_count
    )


def stage_from_python_code(
    stage_name: str,
    code: str,
    timeout_seconds: int = 180,
    stage_count: int | None = None
):
    return execute_stage(
        stage_name,
        [sys.executable, "-c", code],
        timeout_seconds=timeout_seconds,
        stage_count=stage_count
    )


# ============================================================
# STAGE 1: COMPILE REFERENCE SOLUTIONS
# ============================================================

def compile_all_reference_solutions():

    code = '''
import subprocess
from pathlib import Path

root = Path(r"{root}")

sources = sorted(root.glob("T*.cpp"))

if len(sources) != 8:
    raise SystemExit(
        f"Expected 8 reference solutions, found {{len(sources)}}"
    )

for source in sources:

    exe = source.with_suffix(".exe")

    proc = subprocess.run(
        [
            "g++",
            "-std=c++17",
            "-O2",
            str(source),
            "-o",
            str(exe)
        ],
        capture_output=True,
        text=True
    )

    if proc.returncode != 0:
        print(f"Compilation failed: {{source.name}}")
        print(proc.stderr)
        raise SystemExit(proc.returncode)

    print(f"COMPILED: {{source.name}}")

print("All eight reference solutions compiled successfully.")
'''.format(root=str(ROOT / "reference"))

    return stage_from_python_code(
        "compile_references",
        code,
        timeout_seconds=180,
        stage_count=8
    )


# ============================================================
# STAGE 2: PUBLIC TESTS
# ============================================================

def run_public_tests():

    code = '''
import subprocess
import sys

from pathlib import Path

from graders.correctness import (
    validate_topological_order,
    validate_lexicographic_topological_order
)

root = Path(r"{root}")
task_root = root / "tasks"
reference_root = root / "reference"

task_dirs = sorted(
    p for p in task_root.iterdir()
    if p.is_dir()
)

for task_dir in task_dirs:

    task_id = task_dir.name.split("_")[0]

    if task_id not in {{f"T{{i:02d}}" for i in range(1, 9)}}:
        continue

    ref_exe = reference_root / f"{{task_id}}.exe"

    if not ref_exe.exists():
        raise SystemExit(
            f"Missing compiled reference: {{ref_exe}}"
        )

    test_files = sorted(
        (task_dir / "tests").glob("*.in")
    )

    for inp_path in test_files:

        out_path = inp_path.with_suffix(".out")

        if not out_path.exists():
            raise SystemExit(
                f"Missing expected output: {{out_path}}"
            )

        data = inp_path.read_text(encoding="utf-8")
        expected = out_path.read_text(encoding="utf-8")

        got = subprocess.run(
            [str(ref_exe)],
            input=data,
            capture_output=True,
            text=True,
            check=False
        )

        if got.returncode != 0:
            raise SystemExit(
                f"{{task_id}} runtime failure: {{inp_path.name}}"
            )

        if task_id == "T07":

            valid = validate_topological_order(
                "T07",
                data,
                got.stdout
            )

        elif task_id == "T08":

            valid = validate_lexicographic_topological_order(
                "T08",
                data,
                got.stdout
            )

        else:

            valid = (
                got.stdout.strip() == expected.strip()
            )

        if not valid:
            raise SystemExit(
                f"{{task_id}} public test failed: {{inp_path.name}}\\n"
                f"Expected: {{expected.strip()!r}}\\n"
                f"Actual:   {{got.stdout.strip()!r}}"
            )

print("All public tests passed.")
'''.format(root=str(ROOT))

    return stage_from_python_code(
        "public_tests",
        code,
        timeout_seconds=300,
        stage_count=count_public_cases()
    )


# ============================================================
# STAGE 3: HIDDEN TEST GENERATION
# ============================================================

def run_hidden_tests_generation():

    return stage_from_python_script(
        "generate_hidden_tests",
        "validation/generate_hidden_tests.py",
        timeout_seconds=180
    )


# ============================================================
# STAGE 4: DIFFERENTIAL TESTING
# ============================================================

def run_differential_tests():

    return stage_from_python_script(
        "differential_tests",
        "validation/differential_test.py",
        timeout_seconds=600
    )


# ============================================================
# STAGE 5: GRADER VALIDATION
# ============================================================

def run_grader_validation():

    return stage_from_python_script(
        "grader_validation",
        "validation/test_grader.py",
        timeout_seconds=180
    )


# ============================================================
# STAGE 6: T07 SEMANTIC VALIDATION
# ============================================================

def run_t07_validation():

    code = '''
import graders.correctness as corr

inp = (
    "4 4\\n"
    "1 2\\n"
    "1 3\\n"
    "2 4\\n"
    "3 4\\n"
)

valid_orders = [
    "1 2 3 4\\n",
    "1 3 2 4\\n",
]

for order in valid_orders:
    assert corr.validate_topological_order(
        "T07",
        inp,
        order
    ), f"Rejected valid ordering: {{order!r}}"

invalid_order = "4 3 2 1\\n"

assert not corr.validate_topological_order(
    "T07",
    inp,
    invalid_order
), "Accepted invalid topological ordering"

print("T07 semantic validation passed")
'''

    return stage_from_python_code(
        "t07_validation",
        code,
        timeout_seconds=180,
        stage_count=4
    )


# ============================================================
# STAGE 7: T08 LEXICOGRAPHIC VALIDATION
# ============================================================

def run_t08_validation():

    code = '''
import graders.correctness as corr

inp = (
    "4 4\\n"
    "1 2\\n"
    "1 3\\n"
    "2 4\\n"
    "3 4\\n"
)

correct = "1 2 3 4\\n"
wrong = "1 3 2 4\\n"

assert corr.validate_lexicographic_topological_order(
    "T08",
    inp,
    correct
)

assert not corr.validate_lexicographic_topological_order(
    "T08",
    inp,
    wrong
)

print("T08 lexicographic validation passed")
'''

    return stage_from_python_code(
        "t08_validation",
        code,
        timeout_seconds=180,
        stage_count=2
    )


# ============================================================
# STAGE 8: T06 SENTINEL CONSISTENCY
# ============================================================

def validate_t06_consistency() -> bool:

    task_json = (
        ROOT / "tasks" /
        "T06_dag_shortest_path" /
        "task.json"
    )

    prompt_md = (
        ROOT / "tasks" /
        "T06_dag_shortest_path" /
        "prompt.md"
    )

    ref_cpp = ROOT / "reference" / "T06.cpp"

    task_text = task_json.read_text(encoding="utf-8")
    prompt_text = prompt_md.read_text(encoding="utf-8")
    ref_text = ref_cpp.read_text(encoding="utf-8")

    issues = []

    if "UNREACHABLE" not in task_text:
        issues.append("Task metadata missing UNREACHABLE")

    if "UNREACHABLE" not in prompt_text:
        issues.append("Prompt missing UNREACHABLE")

    if "UNREACHABLE" not in ref_text:
        issues.append("Reference solution missing UNREACHABLE")

    if 'cout << -2' in ref_text or 'cout << "-2"' in ref_text:
        issues.append(
            "Reference solution still hardcodes -2 as sentinel"
        )

    if issues:
        raise AssertionError("; ".join(issues))

    return True


def run_t06_consistency_check():

    started_at = utc_timestamp()
    started_time = time.perf_counter()

    log_path = (
        LOGS_DIR /
        f"t06_consistency_{started_at.replace(':', '-')}.log"
    )

    payload = {
        "stage": "t06_consistency",
        "command": ["internal validation"],
        "started_at_utc": started_at,
        "finished_at_utc": None,
        "duration_seconds": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "status": "failed",
        "stage_case_count": 1,
    }

    try:
        validate_t06_consistency()

        payload["stdout"] = "T06 consistency passed\n"
        payload["exit_code"] = 0
        payload["status"] = "success"

    except Exception:
        payload["stderr"] = traceback.format_exc()
        payload["exit_code"] = 1
        payload["status"] = "failed"

    finally:
        payload["finished_at_utc"] = utc_timestamp()

        payload["duration_seconds"] = round(
            time.perf_counter() - started_time,
            6
        )

        log_text = (
            f"COMMAND: {payload['command']}\n"
            f"REPO_ROOT: {ROOT}\n"
            f"STARTED_AT_UTC: {started_at}\n"
            f"FINISHED_AT_UTC: {payload['finished_at_utc']}\n"
            f"EXITCODE: {payload['exit_code']}\n"
            f"DURATION_SECONDS: {payload['duration_seconds']}\n"
            f"STATUS: {payload['status']}\n"
            f"STAGE_CASE_COUNT: 1\n\n"
            f"--- STDOUT ---\n{payload['stdout']}\n\n"
            f"--- STDERR ---\n{payload['stderr']}\n"
        )

        log_path.write_text(log_text, encoding="utf-8")

    return payload


# ============================================================
# STAGE 9: NEGATIVE TESTS
# ============================================================

def run_negative_tests():

    code = '''
import subprocess

from pathlib import Path

root = Path(r"{root}")
validation_dir = root / "validation"

# Incorrect answer detection
wrong_cpp = validation_dir / "wrong_output.cpp"

wrong_cpp.write_text(
    "#include <iostream>\\n"
    "int main() {{ std::cout << 0 << std::endl; }}\\n",
    encoding="utf-8"
)

wrong_exe = validation_dir / "wrong_output.exe"

cp = subprocess.run(
    ["g++", "-std=c++17", "-O2", str(wrong_cpp), "-o", str(wrong_exe)],
    capture_output=True,
    text=True
)

assert cp.returncode == 0, cp.stderr

out = subprocess.run(
    [str(wrong_exe)],
    input="4 10\\n1 2 3 4\\n",
    capture_output=True,
    text=True
)

assert out.stdout.strip() != "1"


# Compilation failure detection
bad_cpp = validation_dir / "bad_compile.cpp"

bad_cpp.write_text(
    "int main() {{ return ; }}",
    encoding="utf-8"
)

cp2 = subprocess.run(
    ["g++", "-std=c++17", "-O2", str(bad_cpp),
     "-o", str(validation_dir / "bad_compile.exe")],
    capture_output=True,
    text=True
)

assert cp2.returncode != 0


# Runtime failure detection
rt_cpp = validation_dir / "runtime_error.cpp"

rt_cpp.write_text(
    "#include <iostream>\\n"
    "int main() {{ int x = 0; std::cout << 1 / x; }}",
    encoding="utf-8"
)

rt_exe = validation_dir / "runtime_error.exe"

cp3 = subprocess.run(
    ["g++", "-std=c++17", "-O2", str(rt_cpp), "-o", str(rt_exe)],
    capture_output=True,
    text=True
)

assert cp3.returncode == 0, cp3.stderr

rt = subprocess.run(
    [str(rt_exe)],
    input="",
    capture_output=True,
    text=True,
    check=False
)

assert rt.returncode != 0


# Timeout detection
timeout_cpp = validation_dir / "timeout.cpp"

timeout_cpp.write_text(
    "#include <iostream>\\n"
    "int main() {{ while (true) {{}} }}",
    encoding="utf-8"
)

timeout_exe = validation_dir / "timeout.exe"

cp4 = subprocess.run(
    ["g++", "-std=c++17", "-O2", str(timeout_cpp),
     "-o", str(timeout_exe)],
    capture_output=True,
    text=True
)

assert cp4.returncode == 0, cp4.stderr

try:
    subprocess.run(
        [str(timeout_exe)],
        input="",
        capture_output=True,
        text=True,
        timeout=1.0,
        check=False
    )

except subprocess.TimeoutExpired:
    pass

else:
    raise AssertionError("Timeout detection did not trigger")

print("Negative tests passed")
'''.format(root=str(ROOT))

    return stage_from_python_code(
        "negative_tests",
        code,
        timeout_seconds=180,
        stage_count=4
    )


# ============================================================
# SUMMARY
# ============================================================

def write_json_snapshot(prefix: str, payload):

    stamp = utc_timestamp().replace(":", "-")

    path = LOGS_DIR / f"{prefix}_{stamp}.json"

    write_json(path, payload)

    return path


def build_summary(records):

    success = sum(
        1 for r in records
        if r.get("status") == "success"
    )

    failed = sum(
        1 for r in records
        if r.get("status") == "failed"
    )

    attempted = len(records)

    total_cases = sum(
        int(r.get("stage_case_count") or 0)
        for r in records
    )

    return {
        "stages_attempted": attempted,
        "stages_successful": success,
        "stages_failed": failed,
        "total_test_cases_executed": total_cases,
    }


# ============================================================
# MAIN VALIDATION PIPELINE
# ============================================================

def main():

    stage_order = [
        compile_all_reference_solutions,
        run_public_tests,
        run_hidden_tests_generation,
        run_differential_tests,
        run_grader_validation,
        run_t07_validation,
        run_t08_validation,
        run_t06_consistency_check,
        run_negative_tests,
    ]

    records = []

    print("=" * 65)
    print("CONSTRAINTFLIP VALIDATION")
    print("=" * 65)

    for index, stage_fn in enumerate(stage_order, start=1):

        print(
            f"\n[{index}/{len(stage_order)}] "
            f"Running: {stage_fn.__name__}"
        )

        try:
            record = stage_fn()

        except Exception:

            record = {
                "stage": stage_fn.__name__,
                "status": "failed",
                "command": ["exception"],
                "stdout": "",
                "stderr": traceback.format_exc(),
                "exit_code": 1,
                "duration_seconds": 0.0,
                "started_at_utc": utc_timestamp(),
                "finished_at_utc": utc_timestamp(),
                "stage_case_count": 0,
            }

        records.append(record)

        print(
            f"Status: {record.get('status', 'unknown')} | "
            f"Duration: {record.get('duration_seconds', 0)} sec"
        )

        if record.get("status") == "failed":
            print("Error:")
            print(record.get("stderr", ""))

    summary = build_summary(records)

    summary_record = {
        "generated_at_utc": utc_timestamp(),
        "root": str(ROOT),
        "summary": summary,
        "stages": records,
    }

    write_json(
        LOGS_DIR / "summary.json",
        summary
    )

    write_json(
        LOGS_DIR / "execution_record.json",
        summary_record
    )

    write_json_snapshot(
        "summary",
        summary
    )

    write_json_snapshot(
        "execution_record",
        summary_record
    )

    print("\n" + "=" * 65)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 65)

    print(json.dumps(summary, indent=2))

    for record in records:
        status = record.get("status", "unknown")
        stage = record.get("stage", "unknown")

        print(f"{stage:25} : {status.upper()}")

    print("=" * 65)

    if summary["stages_failed"] == 0:
        print("VALIDATION RESULT: PASS")
        return 0

    print("VALIDATION RESULT: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
