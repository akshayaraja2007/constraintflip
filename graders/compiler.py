import os
import shutil
import subprocess
import time
from typing import Dict, Optional


def detect_compiler() -> str:
    candidates = [
        os.environ.get("CPP_COMPILER"),
        os.environ.get("CXX"),
        "g++",
        "g++-13",
        "g++-12",
        "g++-11",
        "clang++",
        "c++",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if shutil.which(candidate):
            return candidate
    raise RuntimeError("No C++ compiler found on PATH. Install MinGW-w64 or GCC.")


def compile_cpp(source_path: str, output_path: str, timeout_seconds: float = 20.0) -> Dict[str, object]:
    compiler = detect_compiler()
    start = time.time()
    try:
        result = subprocess.run(
            [compiler, "-std=c++17", "-O2", source_path, "-o", output_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration = time.time() - start
        return {
            "ok": result.returncode == 0,
            "compiler": compiler,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_seconds": duration,
            "output_path": output_path,
            "source_path": source_path,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "compiler": compiler,
            "returncode": None,
            "stdout": "",
            "stderr": f"Compilation timed out after {timeout_seconds} seconds.",
            "duration_seconds": time.time() - start,
            "output_path": output_path,
            "source_path": source_path,
            "timed_out": True,
        }
    except FileNotFoundError:
        return {
            "ok": False,
            "compiler": compiler,
            "returncode": None,
            "stdout": "",
            "stderr": "Compiler not found.",
            "duration_seconds": time.time() - start,
            "output_path": output_path,
            "source_path": source_path,
        }
