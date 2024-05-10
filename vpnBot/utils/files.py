import os
from pathlib import Path


async def delete_file(path: Path):
    if path.exists():
        try:
            os.remove(path)
        except Exception:
            pass
