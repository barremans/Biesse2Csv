from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent / "app" / "version.py"


def main() -> int:
    part = sys.argv[1].lower() if len(sys.argv) > 1 else "patch"

    if part not in {"patch", "minor", "major"}:
        print("[FOUT] Gebruik: patch, minor of major")
        return 1

    text = VERSION_FILE.read_text(encoding="utf-8")

    match = re.search(
        r'__version__\s*=\s*"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"',
        text,
    )

    if not match:
        print(f"[FOUT] __version__ niet gevonden in {VERSION_FILE}")
        return 1

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    text = re.sub(
        r'__version__\s*=\s*"\d+\.\d+\.\d+"',
        f'__version__ = "{new_version}"',
        text,
        count=1,
    )

    VERSION_FILE.write_text(text, encoding="utf-8")
    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
