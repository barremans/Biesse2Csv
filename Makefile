# Makefile
# Beschrijving: Development shortcuts
# Applicatie: Biesse2Csv
# Versie: 1.0.0
# Auteur: Barremans

# Makefile voor Biesse2Csv

.PHONY: install test lint format clean run build help

help:
	@echo "Beschikbare commando's:"
	@echo "  make install   - Installeer dependencies"
	@echo "  make dev       - Installeer dev dependencies"
	@echo "  make test      - Run tests"
	@echo "  make coverage  - Run tests met coverage"
	@echo "  make lint      - Run linters"
	@echo "  make format    - Format code met black"
	@echo "  make clean     - Verwijder cache bestanden"
	@echo "  make run       - Run applicatie"
	@echo "  make build     - Build distributie"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=app --cov=i18n --cov-report=html --cov-report=term

lint:
	flake8 app helpers utils i18n tests
	mypy app helpers utils i18n

format:
	black app helpers utils i18n tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ htmlcov/ 2>/dev/null || true

run:
	python app/main.py

build:
	python setup.py sdist bdist_wheel
