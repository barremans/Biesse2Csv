"""
================================================================================
Module:     i18n/translator.py
Project:    Biesse2Csv
Versie:     1.1.0
Datum:      2026-08-24
Auteur:     Bart Bossuyt

Doel:       Centrale vertaalmodule voor de Biesse2Csv GUI.
            Laadt vertalingen uit JSON-bestanden en maakt het mogelijk om
            tijdens runtime van taal te wisselen.

Wijzigingen:
  v1.0.0 (2026-08-24)  Basisversie van de vertaalmodule.
  v1.1.0 (2026-08-24)  Ondersteuning toegevoegd voor JSON-locales,
                       taalwissel tijdens runtime, fallback-vertalingen
                       en beschikbare talen.
================================================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Translator:
    """Beheert de vertalingen van de applicatie."""

    DEFAULT_LANGUAGE = "nl_NL"

    LANGUAGE_NAMES = {
        "nl_NL": "Nederlands",
        "en_US": "English",
        "fr_FR": "Français",
        "de_DE": "Deutsch",
        "es_ES": "Español",
    }

    def __init__(
        self,
        locales_dir: Path | str,
        language: str = DEFAULT_LANGUAGE,
    ) -> None:
        """
        Initialiseer de translator.

        Args:
            locales_dir:
                Map waarin de JSON-vertaalbestanden staan.

            language:
                Taalcode die bij het starten geladen moet worden.
                Bijvoorbeeld 'nl_NL'.
        """
        self.locales_dir = Path(locales_dir)

        self.language = self.DEFAULT_LANGUAGE

        self._translations: dict[str, Any] = {}
        self._fallback_translations: dict[str, Any] = {}

        self._load_fallback_language()
        self.set_language(language)

    def _load_json(
        self,
        language: str,
    ) -> dict[str, Any]:
        """
        Laad een JSON-taalbestand.

        Args:
            language:
                Taalcode, bijvoorbeeld 'nl_NL'.

        Returns:
            Dictionary met vertalingen.
        """
        language_file = (
            self.locales_dir / f"{language}.json"
        )

        if not language_file.exists():
            return {}

        try:
            with language_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {}

        if not isinstance(data, dict):
            return {}

        return data

    def _load_fallback_language(self) -> None:
        """Laad de standaardtaal als fallback."""
        self._fallback_translations = self._load_json(
            self.DEFAULT_LANGUAGE
        )

    def set_language(
        self,
        language: str,
    ) -> bool:
        """
        Wijzig de actieve taal.

        Args:
            language:
                Nieuwe taalcode.

        Returns:
            True wanneer de taal succesvol geladen werd.
            False wanneer het taalbestand niet gevonden of ongeldig is.
        """
        translations = self._load_json(language)

        if not translations:
            if language != self.DEFAULT_LANGUAGE:
                return False

        self.language = language
        self._translations = translations

        return True

    def tr(
        self,
        key: str,
        default: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Geef de vertaling voor een sleutel terug.

        Voorbeeld:
            translator.tr("main.convert")

        Met variabelen:
            translator.tr(
                "main.files_found",
                count=12
            )

        JSON:
            "main.files_found": "Gevonden bestanden: {count}"

        Resultaat:
            "Gevonden bestanden: 12"
        """
        text = self._get_value(
            self._translations,
            key,
        )

        if text is None:
            text = self._get_value(
                self._fallback_translations,
                key,
            )

        if text is None:
            text = default if default is not None else key

        text = str(text)

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (
                KeyError,
                IndexError,
                ValueError,
            ):
                pass

        return text

    @staticmethod
    def _get_value(
        data: dict[str, Any],
        key: str,
    ) -> Any:
        """
        Zoek een vertaalsleutel.

        Ondersteunt zowel platte JSON:

            "menu.file": "Bestand"

        als geneste JSON:

            {
                "menu": {
                    "file": "Bestand"
                }
            }
        """

        # Eerst rechtstreeks zoeken.
        if key in data:
            return data[key]

        # Daarna geneste structuur proberen.
        value: Any = data

        for part in key.split("."):
            if not isinstance(value, dict):
                return None

            if part not in value:
                return None

            value = value[part]

        return value

    def available_languages(self) -> dict[str, str]:
        """
        Geef alle beschikbare talen terug.

        Alleen talen waarvoor effectief een JSON-bestand bestaat
        worden opgenomen.

        Returns:
            Bijvoorbeeld:
            {
                "nl_NL": "Nederlands",
                "en_US": "English"
            }
        """
        languages: dict[str, str] = {}

        for code, name in self.LANGUAGE_NAMES.items():
            language_file = (
                self.locales_dir / f"{code}.json"
            )

            if language_file.exists():
                languages[code] = name

        return languages

    def current_language(self) -> str:
        """Geef de huidige taalcode terug."""
        return self.language

    def current_language_name(self) -> str:
        """Geef de leesbare naam van de huidige taal terug."""
        return self.LANGUAGE_NAMES.get(
            self.language,
            self.language,
        )