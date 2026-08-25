from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _candidate_paths() -> list[Path]:
    candidates: list[Path] = []

    # 1. PATH
    from_path = shutil.which("signtool.exe")
    if from_path:
        candidates.append(Path(from_path))

    # 2. Windows SDK
    roots = []

    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    if program_files_x86:
        roots.append(
            Path(program_files_x86)
            / "Windows Kits"
            / "10"
            / "bin"
        )

    program_files = os.environ.get("ProgramFiles")
    if program_files:
        roots.append(
            Path(program_files)
            / "Windows Kits"
            / "10"
            / "bin"
        )

    for root in roots:
        if not root.is_dir():
            continue

        # Nieuwste SDK-versie eerst.
        version_dirs = sorted(
            [
                path
                for path in root.iterdir()
                if path.is_dir()
            ],
            reverse=True,
        )

        for version_dir in version_dirs:
            candidate = (
                version_dir
                / "x64"
                / "signtool.exe"
            )

            if candidate.is_file():
                candidates.append(candidate)

    # 3. App Certification Kit
    if program_files_x86:
        candidates.append(
            Path(program_files_x86)
            / "Windows Kits"
            / "10"
            / "App Certification Kit"
            / "signtool.exe"
        )

    return candidates


def main() -> int:
    if len(sys.argv) != 2:
        return 1

    output_file = Path(sys.argv[1])

    for candidate in _candidate_paths():
        if candidate.is_file():
            output_file.write_text(
                str(candidate),
                encoding="utf-8",
            )
            return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())