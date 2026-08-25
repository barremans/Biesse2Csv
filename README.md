<!--
README.md

Beschrijving: Project documentatie
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
-->

# Biesse2Csv

**Versie:** 1.0.0  
**Auteur:** Barremans

## 📋 Beschrijving

omzetten van M520 files die aangeleverd worden door Biesse

## 🌍 Meertaligheid

Deze applicatie ondersteunt de volgende talen:
- 🇳🇱 Nederlands (nl_NL)
- 🇺🇸 English (en_US)
- 🇫🇷 Français (fr_FR)
- 🇩🇪 Deutsch (de_DE)
- 🇪🇸 Español (es_ES)

Zie `i18n/README.md` voor meer informatie.

## 🚀 Installatie

### Vereisten
- Python 3.11 of hoger
- pip package manager

### Productie installatie
```bash
pip install biesse2csv
```

### Development setup
1. Clone de repository
2. Maak een virtuele omgeving aan:
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
```
3. Installeer in development mode:
```bash
   pip install -e ".[dev]"
```

## 💻 Gebruik

### Via command line
```bash
biesse2csv
```

### Als module
```bash
python -m app.main
```

### Development
```bash
make run
```

## 📁 Projectstructuur
```
Biesse2Csv/
├── pyproject.toml # Project configuratie (PEP 621)
├── setup.py       # Backwards compatibility
├── MANIFEST.in    # Package manifest
├── LICENSE        # MIT License
├── README.md
├── requirements.txt
├── .gitignore
├── app/           # Hoofd applicatie code
├── assets/        # Icons en afbeeldingen
│   └── icons/     # Standaard icons
├── config/        # Configuratie bestanden
├── css/           # QSS stylesheets
├── data/          # Data opslag
├── docs/          # Documentatie
├── helpers/       # Helper functies
├── i18n/          # Internationalization
│   ├── translator.py
│   └── locales/   # Vertaalbestanden
├── md/            # Markdown bestanden
├── scripts/       # Utility scripts
├── utils/         # Utility functies
└── tests/         # Unit tests
```

## 🎨 Styling

QSS (Qt StyleSheets) bestanden bevinden zich in `css/`:
- `main.qss` - Hoofd styling
- `detail.qss` - Detail window styling

Laad een stylesheet:
```python
from pathlib import Path

def load_stylesheet(name: str) -> str:
    qss_file = Path("css") / name
    return qss_file.read_text()

app.setStyleSheet(load_stylesheet("main.qss"))
```

## 🌍 Internationalization (i18n)

Gebruik de translator in je code:
```python
from i18n import t

# Simpele vertaling
print(t("app.welcome"))

# Met variabelen
print(t("app.greeting", name="Jan"))
```

Zie `i18n/README.md` voor gedetailleerde documentatie.

## 🔧 Scripts

De `scripts/` folder bevat utility scripts:
- `update_toml.py` - Update pyproject.toml
- `bump_version.py` - Verhoog versie
- `generate_requirements.py` - Genereer requirements.txt
- `validate_project.py` - Valideer project

Zie `scripts/README.md` voor details.

## 🧪 Tests
```bash
# Run alle tests
make test

# Met coverage
make coverage

# Alleen specifieke test
pytest tests/test_specific.py -v
```

## 🛠️ Development

### Code formatting
```bash
make format
```

### Linting
```bash
make lint
```

### Build distributie
```bash
make build
```

## 📝 Changelog

Zie [CHANGELOG.md](docs/changelog.md) voor versiegeschiedenis.

## 🤝 Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen.

## 📄 Licentie

Dit project is gelicenseerd onder de MIT License - zie [LICENSE](LICENSE) voor details.

## 👤 Contact

**Barremans**

## 🙏 Acknowledgments

- Python Community
- PyQt6 Team
