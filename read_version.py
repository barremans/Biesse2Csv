from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent / "app" / "version.py"


def main() -> int:
    if len(sys.argv) != 2:
        print("[FOUT] Gebruik: read_version.py <outputbestand>")
        return 1

    output_file = Path(sys.argv[1])
    text = VERSION_FILE.read_text(encoding="utf-8")

    match = re.search(
        r'__version__\s*=\s*["\'](?P<v>\d+\.\d+\.\d+)["\']',
        text,
    )

    if not match:
        print("[FOUT] Kon __version__ niet vinden.")
        return 1

    output_file.write_text(match.group("v"), encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
