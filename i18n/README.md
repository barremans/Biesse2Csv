<!--
i18n\README.md

Beschrijving: i18n documentatie
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
-->

# Internationalization (i18n)

Deze folder bevat de meertaligheid support voor de applicatie.

## 📁 Structuur
```
i18n/
├── __init__.py
├── translator.py          # Translation helper class
├── locales/              # Vertaalbestanden
│   ├── nl_NL.json       # Nederlands
│   ├── en_US.json       # Engels (fallback)
│   ├── fr_FR.json       # Frans
│   ├── de_DE.json       # Duits
│   └── es_ES.json       # Spaans
└── README.md            # Deze file
```

## 🚀 Gebruik

### Basis gebruik
```python
from i18n import t

# Simpele vertaling
print(t("app.welcome"))  # "Welkom bij Mijn Applicatie!"

# Met variabelen
print(t("app.greeting", name="Jan"))  # "Hallo, Jan!"
```

### Taal wijzigen
```python
from i18n import get_translator

# Start met Nederlands
translator = get_translator("nl_NL")
print(translator.get("button.ok"))  # "OK"

# Wissel naar Frans
translator.set_locale("fr_FR")
print(translator.get("button.ok"))  # "OK" (zelfde in Frans)
```

### In PyQt6
```python
from PyQt6.QtWidgets import QPushButton
from i18n import t

# Buttons
btn_ok = QPushButton(t("button.ok"))
btn_cancel = QPushButton(t("button.cancel"))

# Menu
file_menu = menubar.addMenu(t("menu.file"))
```

## 📝 Nieuwe taal toevoegen

1. Maak nieuw bestand in `locales/`:
```bash
   locales/it_IT.json  # Italiaans
```

2. Kopieer structuur van `en_US.json`

3. Vertaal alle strings:
```json
   {
       "app.welcome": "Benvenuto in {app_name}!",
       "button.ok": "OK",
       "button.cancel": "Annulla"
   }
```

4. Gebruik in je app:
```python
   translator = get_translator("it_IT")
```

## 🔑 Translation Keys

### Conventies:
- **Lowercase** met **dots** als separator
- **Logische groepering**: `categorie.subcategorie.item`
- **Beschrijvend**: `button.save` niet `btn1`

### Voorbeelden:
```
app.name                    # Applicatie naam
app.welcome                 # Welkomstbericht
menu.file.save             # Menu > File > Save
button.ok                  # OK knop
message.confirm_delete     # Bevestigingsbericht
error.file_not_found       # Foutmelding
```

## 🌍 Beschikbare Locales

| Code | Taal | Status |
|------|------|--------|
| `en_US` | English (US) | ✅ Complete (fallback) |
| `nl_NL` | Nederlands | ✅ Complete |
| `fr_FR` | Français | ✅ Complete |
| `de_DE` | Deutsch | ✅ Complete |
| `es_ES` | Español | ✅ Complete |

## 🔧 Advanced

### Format strings

Gebruik `{variable}` voor dynamische waarden:
```json
{
    "app.greeting": "Hallo, {name}!",
    "app.version": "Versie {version}",
    "message.save_error": "Fout: {error}"
}
```
```python
t("app.greeting", name="Jan")        # "Hallo, Jan!"
t("app.version", version="1.0.0")    # "Versie 1.0.0"
```

### Fallback systeem

1. Probeer gekozen locale (bijv. `nl_NL`)
2. Fallback naar Engels (`en_US`)
3. Return de key zelf als laatste optie

### Taal detectie
```python
import locale

# Systeem locale detecteren
system_locale = locale.getdefaultlocale()[0]  # bijv. "nl_NL"
translator = get_translator(system_locale)
```

## 📚 Best Practices

### ✅ DO:
- Gebruik beschrijvende keys
- Groepeer gerelateerde vertalingen
- Test alle talen regelmatig
- Houd vertalingen consistent

### ❌ DON'T:
- Hardcode strings in code
- Gebruik cijfers als keys (`msg1`, `msg2`)
- Vergeet variabelen in format strings
- Mix talen in één bestand

## 🐛 Troubleshooting

### Key niet gevonden
```python
# Returns de key zelf
t("non.existent.key")  # "non.existent.key"
```

### Locale bestand niet gevonden
```python
# Falls back naar en_US
translator = get_translator("xx_XX")  # Gebruikt Engels
```

### Format error
```python
# Ignoreert missing variabelen
t("app.greeting")  # "Hallo, {name}!" (variabele niet replaced)
```

## 📖 Meer info

- [Python i18n Best Practices](https://docs.python.org/3/library/i18n.html)
- [Locale Codes (ISO 639-1 + ISO 3166-1)](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
