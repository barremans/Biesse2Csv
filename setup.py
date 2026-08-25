"""
setup.py

Beschrijving: Setup script (backwards compatibility)
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans
"""

"""
setup.py

Beschrijving: Package setup (backwards compatibility)
Applicatie: Biesse2Csv
Versie: 1.0.0
Auteur: Barremans

Note: Dit bestand is voor backwards compatibility.
De primaire configuratie staat in pyproject.toml
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lees version uit app/version.py
version = "1.0.0"
try:
    with open("app/version.py", "r") as f:
        exec(f.read())
        version = __version__  # noqa: F821
except Exception:
    pass

# Lees README
long_description = ""
readme_file = Path("README.md")
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Lees requirements
requirements = []
req_file = Path("requirements.txt")
if req_file.exists():
    with open(req_file, "r") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="biesse2csv",
    version=version,
    author="Barremans",
    description="omzetten van M520 files die aangeleverd worden door Biesse",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    install_requires=requirements,
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "biesse2csv=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "i18n": ["locales/*.json"],
    },
)
