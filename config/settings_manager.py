"""
================================================================================
Module:     config/settings_manager.py
Project:    Biesse2Csv
Versie:     1.1.0
Datum:      2026-08-24
Auteur:     Bart Bossuyt

Doel:       Beheer van de applicatie-instellingen via JSON.
            Laadt standaardinstellingen, leest settings.json in en bewaart
            wijzigingen naar schijf.

Wijzigingen:
  v1.0.0 (2026-08-24)  Initiële versie — JSON-instellingenbeheer met
                       standaardwaarden, laden, opslaan, get en set.
  v1.1.0 (2026-08-24)  Metadata en versie-informatie toegevoegd aan de
                       standaard JSON-instellingen.
================================================================================
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """Beheert de instellingen van Biesse2Csv via een JSON-bestand."""

    DEFAULT_SETTINGS = {
        "meta": {
            "project": "Biesse2Csv",
            "version": "1.0.0",
            "date": "2026-08-24",
            "author": "Bart Bossuyt",
            "description": "Applicatie-instellingen voor Biesse2Csv",
            "changes": [
                {
                    "version": "1.0.0",
                    "date": "2026-08-24",
                    "description": (
                        "Initiële versie met taal-, map- en "
                        "conversie-instellingen."
                    )
                }
            ]
        },
        "general": {
            "language": "nl_NL"
        },
        "folders": {
            "input_folder": "",
            "output_folder": ""
        },
        "conversion": {
            "delimiter": ";",
            "encoding": "utf-8-sig",
            "overwrite_existing": False
        }
    }

    def __init__(self, settings_file: Path | str) -> None:
        """
        Initialiseer de settings manager.

        Args:
            settings_file:
                Pad naar het JSON-bestand waarin de instellingen
                worden opgeslagen.
        """
        self.settings_file = Path(settings_file)
        self.settings = self._load()

    def _load(self) -> dict[str, Any]:
        """
        Laad de instellingen vanaf schijf.

        Wanneer het bestand niet bestaat, worden de standaardinstellingen
        aangemaakt en opgeslagen.
        """
        if not self.settings_file.exists():
            settings = copy.deepcopy(self.DEFAULT_SETTINGS)
            self._write(settings)
            return settings

        try:
            with self.settings_file.open(
                "r",
                encoding="utf-8"
            ) as file:
                loaded_settings = json.load(file)

        except (OSError, json.JSONDecodeError):
            return copy.deepcopy(self.DEFAULT_SETTINGS)

        return self._merge_defaults(
            self.DEFAULT_SETTINGS,
            loaded_settings
        )

    def save(self) -> None:
        """Sla de huidige instellingen op naar het JSON-bestand."""
        self._write(self.settings)

    def _write(self, settings: dict[str, Any]) -> None:
        """
        Schrijf instellingen naar schijf.

        De config-map wordt automatisch aangemaakt indien nodig.
        """
        self.settings_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.settings_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                settings,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get(
        self,
        section: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Lees een instelling.

        Voorbeeld:
            settings.get("folders", "input_folder")
        """
        return self.settings.get(
            section,
            {}
        ).get(
            key,
            default
        )

    def set(
        self,
        section: str,
        key: str,
        value: Any,
        *,
        save: bool = False
    ) -> None:
        """
        Wijzig een instelling.

        Args:
            section:
                Hoofdsectie, bijvoorbeeld 'folders'.

            key:
                Instelling binnen de sectie.

            value:
                Nieuwe waarde.

            save:
                Indien True wordt de wijziging onmiddellijk opgeslagen.
        """
        if section not in self.settings:
            self.settings[section] = {}

        self.settings[section][key] = value

        if save:
            self.save()

    def reset(self) -> None:
        """Herstel alle instellingen naar de standaardwaarden."""
        self.settings = copy.deepcopy(
            self.DEFAULT_SETTINGS
        )

        self.save()

    @staticmethod
    def _merge_defaults(
        defaults: dict[str, Any],
        loaded: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Voeg ontbrekende standaardwaarden toe aan ingelezen instellingen.

        Hierdoor blijven oudere settings.json-bestanden bruikbaar wanneer
        later nieuwe instellingen aan de applicatie worden toegevoegd.
        """
        result = copy.deepcopy(defaults)

        for key, value in loaded.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = SettingsManager._merge_defaults(
                    result[key],
                    value
                )
            else:
                result[key] = value

        return result