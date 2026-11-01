#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(r'c:\Users\acer\OneDrive\Desktop\ConstraintFlip').resolve()
logs_dir = root / 'validation' / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)

probe_path = logs_dir / 'diag_probe.txt'
timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
probe_path.write_text('timestamp=' + timestamp + '\n', encoding='utf-8')
probe_text = probe_path.read_text(encoding='utf-8')

cmd = [sys.executable, '-c', 'import sys; print("STDOUT_OK"); sys.stderr.write("STDERR_OK\\n")']
start = time.perf_counter()
proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
duration = time.perf_counter() - start

log_path = logs_dir / ('diag_run_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.log')
log_path.write_text(
    'cwd=' + str(root) + '\n'
    'logs_dir=' + str(logs_dir) + '\n'
    'probe_exists=' + str(probe_path.exists()) + '\n'
    'probe_read=' + probe_text.strip() + '\n'
    'cmd=' + str(cmd) + '\n'
    'stdout=' + proc.stdout.strip() + '\n'
    'stderr=' + proc.stderr.strip() + '\n'
    'exit_code=' + str(proc.returncode) + '\n'
    'duration_seconds=' + f'{duration:.6f}' + '\n',
    encoding='utf-8'
)

print('CWD=' + str(root))
print('LOGS_DIR=' + str(logs_dir))
print('PROBE_EXISTS=' + str(probe_path.exists()))
print('PROBE_READ=' + probe_text.strip())
print('STDOUT=' + proc.stdout.strip())
print('STDERR=' + proc.stderr.strip())
print('EXIT_CODE=' + str(proc.returncode))
print('DURATION=' + f'{duration:.6f}')
print('LOG_PATH=' + str(log_path))
print('LOG_EXISTS=' + str(log_path.exists()))
print('LOG_READ=' + log_path.read_text(encoding='utf-8').splitlines()[0])
print('FILES=' + str(sorted(p.name for p in logs_dir.iterdir())))
print('READY')
