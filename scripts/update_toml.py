"""
scripts\update_toml.py

Beschrijving: Update pyproject.toml
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
"""

"""
scripts/update_toml.py

Beschrijving: Update pyproject.toml automatisch
Versie: 1.0.5
"""

import argparse
import sys
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description="Update pyproject.toml")
    parser.add_argument("--add-dep", help="Voeg runtime dependency toe")
    parser.add_argument("--add-dev", help="Voeg dev dependency toe")
    parser.add_argument("--set-version", help="Zet versie nummer")
    parser.add_argument("--set-author", help="Zet auteur naam")
    parser.add_argument("--set-description", help="Zet beschrijving")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    toml_file = project_root / "pyproject.toml"
    
    if not toml_file.exists():
        print(f"❌ Fout: {toml_file} niet gevonden")
        sys.exit(1)
    
    try:
        import tomli
        import tomli_w
    except ImportError:
        print("❌ Fout: tomli en tomli_w zijn vereist")
        print("Installeer met: pip install tomli tomli-w")
        sys.exit(1)
    
    with open(toml_file, "rb") as f:
        data = tomli.load(f)
    
    backup_file = toml_file.with_suffix(".toml.bak")
    shutil.copy2(toml_file, backup_file)
    print(f"📋 Backup gemaakt: {backup_file}")
    
    modified = False
    
    if args.add_dep:
        if "project" not in data:
            data["project"] = {}
        if "dependencies" not in data["project"]:
            data["project"]["dependencies"] = []
        
        if args.add_dep not in data["project"]["dependencies"]:
            data["project"]["dependencies"].append(args.add_dep)
            print(f"✅ Dependency toegevoegd: {args.add_dep}")
            modified = True
        else:
            print(f"ℹ️  Dependency bestaat al: {args.add_dep}")
    
    if args.add_dev:
        if "project" not in data:
            data["project"] = {}
        if "optional-dependencies" not in data["project"]:
            data["project"]["optional-dependencies"] = {}
        if "dev" not in data["project"]["optional-dependencies"]:
            data["project"]["optional-dependencies"]["dev"] = []
        
        if args.add_dev not in data["project"]["optional-dependencies"]["dev"]:
            data["project"]["optional-dependencies"]["dev"].append(args.add_dev)
            print(f"✅ Dev dependency toegevoegd: {args.add_dev}")
            modified = True
    
    if args.set_version:
        if "project" not in data:
            data["project"] = {}
        data["project"]["version"] = args.set_version
        print(f"✅ Versie gezet: {args.set_version}")
        modified = True
    
    if args.set_author:
        if "project" not in data:
            data["project"] = {}
        data["project"]["authors"] = [{"name": args.set_author}]
        print(f"✅ Auteur gezet: {args.set_author}")
        modified = True
    
    if args.set_description:
        if "project" not in data:
            data["project"] = {}
        data["project"]["description"] = args.set_description
        print(f"✅ Beschrijving gezet: {args.set_description}")
        modified = True
    
    if modified:
        with open(toml_file, "wb") as f:
            tomli_w.dump(data, f)
        print(f"💾 {toml_file} is bijgewerkt")
    else:
        print("ℹ️  Geen wijzigingen")
    
    print("✅ Klaar!")


if __name__ == "__main__":
    main()
