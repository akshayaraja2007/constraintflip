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

# write + readback check
probe = logs_dir / 'probe_write_read.txt'
probe.write_text('probe=' + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + '\n', encoding='utf-8')
read_back = probe.read_text(encoding='utf-8')

# subprocess capture check
cmd = [sys.executable, '-c', 'import sys; print("STDOUT_OK"); sys.stderr.write("STDERR_OK\\n")']
start = time.perf_counter()
proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
duration = time.perf_counter() - start

log_name = 'diagnostic_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.log'
log_path = logs_dir / log_name
log_path.write_text(
    'cwd=' + str(root) + '\n'
    'logs_dir=' + str(logs_dir) + '\n'
    'probe_exists=' + str(probe.exists()) + '\n'
    'probe_read=' + read_back.strip() + '\n'
    'cmd=' + str(cmd) + '\n'
    'stdout=' + proc.stdout.strip() + '\n'
    'stderr=' + proc.stderr.strip() + '\n'
    'exit_code=' + str(proc.returncode) + '\n'
    'duration_seconds=' + f'{duration:.6f}' + '\n'
    'timestamp_utc=' + datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + '\n',
    encoding='utf-8'
)

print('cwd=' + str(root))
print('logs_dir=' + str(logs_dir))
print('probe_exists=' + str(probe.exists()))
print('probe_read=' + read_back.strip())
print('cmd=' + str(cmd))
print('stdout=' + proc.stdout.strip())
print('stderr=' + proc.stderr.strip())
print('exit_code=' + str(proc.returncode))
print('duration_seconds=' + f'{duration:.6f}')
print('generated_log=' + str(log_path))
print('generated_files=' + str(sorted(p.name for p in logs_dir.iterdir())))
print('read_back_log=' + log_path.read_text(encoding='utf-8').strip().splitlines()[0])
