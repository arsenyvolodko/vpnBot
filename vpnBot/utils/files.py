import os
from pathlib import Path


def delete_file(path: Path):
    if path.exists():
        try:
            os.remove(path)
        except Exception:
            pass
