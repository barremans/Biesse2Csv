<!--
md\help.md

Beschrijving: Help documentatie
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
-->

# Biesse2Csv - Help

## 📚 Aan de slag

Welkom bij Biesse2Csv!

## ⚙️ Configuratie

De applicatie gebruikt configuratie bestanden in de `config/` folder:
- `settings.json` - Algemene instellingen (incl. default_locale)

## 🎨 Styling

Pas de look-and-feel aan door de QSS bestanden in `css/` te bewerken:
- `main.qss` - Hoofd styling
- `detail.qss` - Detail windows

## 🌍 Talen

De applicatie ondersteunt meerdere talen via het `i18n/` systeem.

### Taal wijzigen
```python
from i18n import get_translator

translator = get_translator("nl_NL")  # Nederlands
translator.set_locale("en_US")        # Wissel naar Engels
```

### Beschikbare talen
- Nederlands (nl_NL)
- English (en_US)
- Français (fr_FR)
- Deutsch (de_DE)
- Español (es_ES)

Zie `i18n/README.md` voor volledige documentatie.

## 🔧 Functies

Beschrijf hier de hoofdfuncties van de applicatie.

### Functie 1
Beschrijving van functie 1.

### Functie 2
Beschrijving van functie 2.

## 🛠️ Development Scripts

De `scripts/` folder bevat utilities:

### update_toml.py
```bash
cd scripts
python update_toml.py --add-dep "requests>=2.31.0"
```

### bump_version.py
```bash
cd scripts
python bump_version.py patch  # 1.0.0 → 1.0.1
```

Zie `scripts/README.md` voor volledige documentatie.

## ❓ Veelgestelde vragen

### Hoe start ik de applicatie?
```bash
python app/main.py
```

### Waar staan de configuratie bestanden?
In de `config/` folder.

### Hoe pas ik de styling aan?
Bewerk de QSS bestanden in de `css/` folder.

### Hoe voeg ik een dependency toe?
```bash
cd scripts
python update_toml.py --add-dep "package-name>=version"
pip install package-name
```

### Hoe voeg ik een nieuwe taal toe?
Zie `i18n/README.md` sectie "Nieuwe taal toevoegen".

## 📞 Contact

Voor vragen of ondersteuning, neem contact op met de ontwikkelaar.
