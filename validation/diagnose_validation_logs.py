#!/usr/bin/env python3
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
logs_dir = root / 'validation' / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)

probe_file = logs_dir / 'diagnostic_probe.txt'
probe_text = f'probe_created_at_utc={datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}\n'
probe_file.write_text(probe_text, encoding='utf-8')
read_back = probe_file.read_text(encoding='utf-8')

cmd = [
    'py',
    '-c',
    'import sys; print("STDOUT_OK"); sys.stderr.write("STDERR_OK\\n"); raise SystemExit(7)'
]
start = time.perf_counter()
proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
duration = time.perf_counter() - start

log_file = logs_dir / f"diagnostic_run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
log_text = (
    f'cwd={root}\n'
    f'logs_dir={logs_dir}\n'
    f'logs_dir_exists={logs_dir.exists()}\n'
    f'logs_dir_writable={os.access(logs_dir, os.W_OK)}\n'
    f'probe_file={probe_file}\n'
    f'probe_file_exists={probe_file.exists()}\n'
    f'probe_file_read_back={read_back.strip()}\n'
    f'command={cmd}\n'
    f'stdout={proc.stdout.strip()}\n'
    f'stderr={proc.stderr.strip()}\n'
    f'exit_code={proc.returncode}\n'
    f'duration_seconds={duration:.6f}\n'
    f'timestamp_utc={datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}\n'
)
log_file.write_text(log_text, encoding='utf-8')

print(f'cwd={root}')
print(f'logs_dir={logs_dir}')
print(f'logs_dir_exists={logs_dir.exists()}')
print(f'logs_dir_writable={os.access(logs_dir, os.W_OK)}')
print(f'probe_file_exists={probe_file.exists()}')
print(f'probe_file_read_back={read_back.strip()}')
print(f'command={cmd}')
print(f'stdout={proc.stdout.strip()}')
print(f'stderr={proc.stderr.strip()}')
print(f'exit_code={proc.returncode}')
print(f'duration_seconds={duration:.6f}')
print(f'generated_log={log_file.name}')
print(f'generated_files={sorted(p.name for p in logs_dir.iterdir())}')
