import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDES = {'.git', '__pycache__', '.venv', 'venv', '.idea', '.pytest_cache'}

def should_exclude(path: Path) -> bool:
    name = path.name
    if name in EXCLUDES:
        return True
    if path.suffix in {'.exe', '.obj', '.o', '.out', '.bin'}:
        return True
    if any(part in {'__pycache__', '.git'} for part in path.parts):
        return True
    return False


def build_zip(output_name: str = 'ConstraintFlip_submission.zip') -> Path:
    output_path = ROOT / output_name
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in ROOT.rglob('*'):
            if file.is_dir():
                continue
            if should_exclude(file):
                continue
            rel = file.relative_to(ROOT)
            zf.write(file, arcname=str(rel))
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f'Created {output_path} ({size_mb:.2f} MB)')
    return output_path


if __name__ == '__main__':
    build_zip()
