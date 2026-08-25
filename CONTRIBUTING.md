<!--
CONTRIBUTING.md

Beschrijving: Contributie richtlijnen
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
-->

# Bijdragen aan Biesse2Csv

Bedankt voor je interesse om bij te dragen!

## Development Setup

1. Clone de repository
2. Maak een virtuele omgeving:
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
```

3. Installeer dependencies (inclusief dev):
```bash
   pip install -e ".[dev]"
```

## Code Style

We gebruiken:
- **Black** voor code formatting (max line length: 100)
- **Flake8** voor linting
- **MyPy** voor type checking

Run deze voor je commit:
```bash
black .
flake8 .
mypy .
```

## Tests

Run alle tests:
```bash
pytest
```

Met coverage:
```bash
pytest --cov=app --cov-report=html
```

## i18n (Vertalingen)

Bij het toevoegen van nieuwe UI teksten:
1. Gebruik `t("key.name")` in plaats van hardcoded strings
2. Voeg de key toe aan alle locale bestanden in `i18n/locales/`
3. Test in meerdere talen

## Commit Messages

Gebruik duidelijke commit messages:
- `feat: add new feature`
- `fix: resolve bug in ...`
- `docs: update README`
- `refactor: improve code structure`
- `test: add tests for ...`
- `i18n: add translations for ...`

## Pull Requests

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/amazing-feature`)
3. Commit je changes (`git commit -m 'feat: add amazing feature'`)
4. Push naar je fork (`git push origin feature/amazing-feature`)
5. Open een Pull Request

## Code Review Process

- Alle PRs moeten reviewed worden
- Tests moeten slagen
- Code style moet kloppen
- Alle talen moeten bijgewerkt zijn

## Vragen?

Open een issue voor vragen of discussies.
