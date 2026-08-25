<!--
scripts\README.md

Beschrijving: Scripts documentatie
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
-->

# Scripts Folder

Utility scripts voor project maintenance en automation.

## 📋 Beschikbare Scripts

### 🔧 update_toml.py
Update `pyproject.toml` automatisch.

**Gebruik:**
```bash
# Voeg dependency toe
python update_toml.py --add-dep "requests>=2.31.0"

# Voeg dev dependency toe
python update_toml.py --add-dev "pytest-cov>=4.1.0"

# Update versie
python update_toml.py --set-version "1.0.1"

# Update auteur
python update_toml.py --set-author "Nieuwe Naam"
```

**Vereisten:** `tomli`, `tomli-w`

---

### 📈 bump_version.py
Verhoog versienummer overal in het project.

**Gebruik:**
```bash
# Patch (1.0.0 → 1.0.1)
python bump_version.py patch

# Minor (1.0.0 → 1.1.0)
python bump_version.py minor

# Major (1.0.0 → 2.0.0)
python bump_version.py major

# Specifieke versie
python bump_version.py --version 2.5.3
```

**Update:**
- `app/version.py`
- `pyproject.toml`
- `docs/changelog.md` (voegt nieuwe sectie toe)

**Vereisten:** `tomli`, `tomli-w` (optioneel, gebruikt regex fallback)

---

### 📦 generate_requirements.py
Genereer `requirements.txt` uit `pyproject.toml`.

**Gebruik:**
```bash
# Alleen runtime dependencies
python generate_requirements.py

# Inclusief dev dependencies
python generate_requirements.py --dev

# Custom output
python generate_requirements.py --output requirements-dev.txt --dev
```

**Vereisten:** `tomli`

---

### ✅ validate_project.py
Valideer project structuur en configuratie.

**Gebruik:**
```bash
python validate_project.py
```

**Controleert:**
- Bestanden en folders aanwezig
- `pyproject.toml` is valide
- Tests runnen (pytest)
- Code style (black)

**Vereisten:** `tomli`, `pytest` (optioneel), `black` (optioneel)

---

## 📦 Dependencies Installeren
```bash
pip install tomli tomli-w pytest black
```

Of gebruik development mode:
```bash
pip install -e ".[dev]"
```

## 💡 Tips

- Run scripts vanuit de `scripts/` folder
- Scripts maken automatisch backups
- Check altijd de output voor errors
- Gebruik `--help` voor meer opties (waar beschikbaar)

## 🐛 Troubleshooting

### tomli/tomli-w not found
```bash
pip install tomli tomli-w
```

### Script vindt pyproject.toml niet
Zorg dat je in de `scripts/` folder staat:
```bash
cd scripts
python update_toml.py ...
```

### Permission errors
Run met admin rechten (Windows) of sudo (Linux)
