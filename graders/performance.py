import subprocess
import time
from typing import Dict, Optional


def run_program(executable_path: str, input_text: str, timeout_seconds: float = 2.0, cwd: Optional[str] = None) -> Dict[str, object]:
    start = time.time()
    try:
        completed = subprocess.run(
            [executable_path],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            cwd=cwd,
        )
        duration = time.time() - start
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "duration_seconds": duration,
            "timed_out": False,
            "runtime_error": completed.returncode != 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Timed out after {timeout_seconds} seconds.",
            "duration_seconds": timeout_seconds,
            "timed_out": True,
            "runtime_error": False,
        }
