"""
================================================================================
Module:     app/main.py
Project:    Biesse2Csv
Versie:     1.2.1
Datum:      2026-08-25
Auteur:     Bart Bossuyt

Doel:       Startpunt van de Biesse2Csv-applicatie.
            Initialiseert QApplication, gebruikersinstellingen, vertalingen,
            applicatie-icoon en het PySide6-hoofdvenster. Ondersteunt zowel
            ontwikkeling vanuit broncode als uitvoering via PyInstaller.

Wijzigingen:
  v1.0.0 (2026-08-24)  Initiële applicatiestart.
  v1.1.0 (2026-08-24)  SettingsManager, Translator en MainWindow gekoppeld.
                       Projectpaden en applicatie-icoon centraal ingesteld.
  v1.2.0 (2026-08-25)  Runtime-resources PyInstaller-safe gemaakt.
                       Gebruikersinstellingen verplaatst naar
                       %APPDATA%\\Biesse2Csv\\settings.json met eenmalige
                       migratie van de oude config\\settings.json.
  v1.2.1 (2026-08-26)  SyntaxWarning voor Windows-paden in docstrings
                       opgelost door backslashes correct te escapen.
================================================================================
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


# ==============================================================================
# Project- en runtimepaden
# ==============================================================================

# Projectroot tijdens ontwikkeling.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Nodig wanneer de applicatie rechtstreeks gestart wordt met:
#
#     python app/main.py
#
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


def _resource_root() -> Path:
    """
    Geef de map terug waarin gebundelde read-only resources staan.

    Tijdens ontwikkeling is dit de projectroot.
    In een PyInstaller-build wijst sys._MEIPASS naar de bundelmap.
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

    return PROJECT_ROOT


def _user_data_dir() -> Path:
    """
    Geef de schrijfbare gebruikersmap voor Biesse2Csv terug.

    Windows:
        %APPDATA%\\Biesse2Csv

    Fallback:
        ~/AppData/Roaming/Biesse2Csv
    """
    appdata = os.environ.get("APPDATA")

    if appdata:
        return Path(appdata) / "Biesse2Csv"

    return (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Biesse2Csv"
    )


RESOURCE_ROOT = _resource_root()
USER_DATA_DIR = _user_data_dir()

SETTINGS_FILE = (
    USER_DATA_DIR
    / "settings.json"
)

LOCALES_DIR = (
    RESOURCE_ROOT
    / "i18n"
    / "locales"
)

ICON_FILE = (
    RESOURCE_ROOT
    / "assets"
    / "icons"
    / "app_icon.ico"
)

# Alleen gebruikt om bestaande ontwikkelinstellingen éénmalig te migreren.
LEGACY_SETTINGS_FILE = (
    PROJECT_ROOT
    / "config"
    / "settings.json"
)


# ==============================================================================
# Applicatie-imports
# ==============================================================================

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from config.settings_manager import SettingsManager
from i18n.translator import Translator


# ==============================================================================
# Instellingenmigratie
# ==============================================================================


def migrate_legacy_settings() -> None:
    """
    Migreer oude projectinstellingen éénmalig naar %APPDATA%.

    Alleen wanneer:
        - de nieuwe settingsfile nog niet bestaat;
        - config/settings.json tijdens ontwikkeling beschikbaar is.

    In een geïnstalleerde PyInstaller-build zal de legacy file normaal
    niet bestaan en maakt SettingsManager automatisch defaults aan.
    """
    if SETTINGS_FILE.exists():
        return

    if not LEGACY_SETTINGS_FILE.is_file():
        return

    try:
        SETTINGS_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            LEGACY_SETTINGS_FILE,
            SETTINGS_FILE,
        )

    except OSError:
        # Niet fataal: SettingsManager kan daarna zelf defaults aanmaken.
        pass


# ==============================================================================
# Applicatie
# ==============================================================================


def create_application() -> QApplication:
    """
    Maak en configureer de Qt-applicatie.

    Returns:
        Geconfigureerde QApplication.
    """

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Biesse2Csv"
    )

    app.setApplicationDisplayName(
        "Biesse2Csv"
    )

    app.setOrganizationName(
        "Bart Bossuyt"
    )

    if ICON_FILE.is_file():
        app.setWindowIcon(
            QIcon(
                str(ICON_FILE)
            )
        )

    return app


def main() -> int:
    """
    Start Biesse2Csv.

    Returns:
        Qt exit-code.
    """

    app = create_application()

    migrate_legacy_settings()

    settings = SettingsManager(
        SETTINGS_FILE
    )

    language = settings.get(
        "general",
        "language",
        Translator.DEFAULT_LANGUAGE,
    )

    translator = Translator(
        locales_dir=LOCALES_DIR,
        language=language,
    )

    if (
        translator.current_language()
        != language
    ):
        translator.set_language(
            Translator.DEFAULT_LANGUAGE
        )

        settings.set(
            "general",
            "language",
            Translator.DEFAULT_LANGUAGE,
            save=True,
        )

    window = MainWindow(
        settings_manager=settings,
        translator=translator,
    )

    if ICON_FILE.is_file():
        window.setWindowIcon(
            QIcon(
                str(ICON_FILE)
            )
        )

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(
        main()
    )