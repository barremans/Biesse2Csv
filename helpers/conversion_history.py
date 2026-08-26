"""
================================================================================
Module:     helpers/conversion_history.py
Project:    Biesse2Csv
Versie:     1.1.0
Datum:      2026-08-26
Auteur:     Bart Bossuyt

Doel:       Permanente historiek bijhouden van succesvol geconverteerde
            Biesse-bronbestanden. De historiek wordt opgeslagen in
            %APPDATA%\\Biesse2Csv\\conversion_history.json en gebruikt
            bestandsomvang en wijzigingsdatum om te detecteren of een eerder
            verwerkt bronbestand nadien gewijzigd werd.

Wijzigingen:
  v1.1.0 (2026-08-26)  Foutstatus en foutmelding toegevoegd. Permanente
                       uitsluiting van bronbestanden toegevoegd zodat
                       deze standaard uit het overzicht gefilterd kunnen worden.
  v1.0.0 (2026-08-26)  Initiële versie — JSON-historiek met statussen
                       niet verwerkt, verwerkt en gewijzigd sinds conversie.
================================================================================
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class ConversionHistory:
    """Beheer de permanente conversiehistoriek van Biesse-bronbestanden."""

    STATUS_NOT_PROCESSED = "not_processed"
    STATUS_PROCESSED = "processed"
    STATUS_MODIFIED = "modified"
    STATUS_ERROR = "error"
    STATUS_EXCLUDED = "excluded"

    HISTORY_VERSION = 1
    APPLICATION_FOLDER = "Biesse2Csv"
    HISTORY_FILENAME = "conversion_history.json"

    def __init__(
        self,
        history_file: Path | str | None = None,
    ) -> None:
        """
        Initialiseer de historiek.

        Args:
            history_file:
                Optioneel expliciet pad, hoofdzakelijk nuttig voor tests.
                Zonder expliciet pad wordt %APPDATA%\\Biesse2Csv gebruikt.
        """
        self.history_file = (
            Path(history_file)
            if history_file is not None
            else self.default_history_file()
        )

        self._data: dict[str, Any] = {
            "version": self.HISTORY_VERSION,
            "files": {},
        }

        self.load()

    @classmethod
    def default_history_file(cls) -> Path:
        """Geef het standaardpad van conversion_history.json terug."""

        appdata = os.environ.get(
            "APPDATA"
        )

        if appdata:
            base_folder = Path(
                appdata
            )

        else:
            # Veilige fallback voor ontwikkel-/testomgevingen waar APPDATA
            # niet beschikbaar is.
            base_folder = (
                Path.home()
                / "AppData"
                / "Roaming"
            )

        return (
            base_folder
            / cls.APPLICATION_FOLDER
            / cls.HISTORY_FILENAME
        )

    def load(self) -> None:
        """Laad de JSON-historiek. Ongeldige data resulteert in een lege historiek."""

        if not self.history_file.is_file():
            return

        try:
            loaded = json.loads(
                self.history_file.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return

        if not isinstance(
            loaded,
            dict,
        ):
            return

        files = loaded.get(
            "files"
        )

        if not isinstance(
            files,
            dict,
        ):
            return

        self._data = {
            "version": loaded.get(
                "version",
                self.HISTORY_VERSION,
            ),
            "files": files,
        }

    def save(self) -> None:
        """Schrijf de historiek atomisch naar JSON."""

        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = self.history_file.with_suffix(
            ".tmp"
        )

        payload = json.dumps(
            self._data,
            indent=4,
            ensure_ascii=False,
        )

        temporary_file.write_text(
            payload,
            encoding="utf-8",
        )

        temporary_file.replace(
            self.history_file
        )

    def get_status(
        self,
        source_file: Path | str,
    ) -> str:
        """
        Bepaal de historiekstatus van een bronbestand.

        Returns:
            not_processed:
                Nog nooit succesvol geconverteerd.

            processed:
                Eerder succesvol geconverteerd en bronbestand sindsdien
                niet gewijzigd.

            modified:
                Eerder succesvol geconverteerd, maar bestandsgrootte of
                wijzigingsdatum wijkt af van de geregistreerde versie.
        """

        source_path = Path(
            source_file
        )

        entry = self._data["files"].get(
            self._source_key(
                source_path
            )
        )

        if not isinstance(
            entry,
            dict,
        ):
            return self.STATUS_NOT_PROCESSED

        if bool(entry.get("excluded", False)):
            return self.STATUS_EXCLUDED

        if entry.get("status") == self.STATUS_ERROR:
            return self.STATUS_ERROR

        try:
            stat = source_path.stat()

        except OSError:
            return self.STATUS_NOT_PROCESSED

        registered_size = entry.get(
            "source_size"
        )

        registered_modified_ns = entry.get(
            "source_modified_ns"
        )

        if (
            registered_size != stat.st_size
            or registered_modified_ns != stat.st_mtime_ns
        ):
            return self.STATUS_MODIFIED

        return self.STATUS_PROCESSED

    def get_processed_at(
        self,
        source_file: Path | str,
    ) -> str:
        """Geef de laatst geregistreerde succesvolle conversiedatum terug."""

        source_path = Path(
            source_file
        )

        entry = self._data["files"].get(
            self._source_key(
                source_path
            )
        )

        if not isinstance(
            entry,
            dict,
        ):
            return ""

        processed_at = entry.get(
            "processed_at",
            "",
        )

        if not isinstance(
            processed_at,
            str,
        ):
            return ""

        try:
            value = datetime.fromisoformat(
                processed_at
            )

        except ValueError:
            return processed_at

        return value.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

    def mark_success(
        self,
        source_file: Path | str,
        csv_file: Path | str,
        xlsx_file: Path | str,
    ) -> None:
        """Registreer een succesvol geconverteerd bronbestand en sla direct op."""

        source_path = Path(
            source_file
        )

        stat = source_path.stat()

        self._data["files"][
            self._source_key(
                source_path
            )
        ] = {
            "source_name": source_path.name,
            "source_path": str(
                source_path.resolve()
            ),
            "source_size": stat.st_size,
            "source_modified_ns": stat.st_mtime_ns,
            "source_modified": datetime.fromtimestamp(
                stat.st_mtime
            ).isoformat(
                timespec="seconds"
            ),
            "processed_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "csv": str(
                Path(csv_file).resolve()
            ),
            "xlsx": str(
                Path(xlsx_file).resolve()
            ),
            "status": "success",
        }

        self.save()


    def mark_error(
        self,
        source_file: Path | str,
        error: str,
    ) -> None:
        """Bewaar een conversiefout zodat de reden later zichtbaar blijft."""

        source_path = Path(source_file)
        key = self._source_key(source_path)

        try:
            stat = source_path.stat()
            source_size = stat.st_size
            source_modified_ns = stat.st_mtime_ns
        except OSError:
            source_size = None
            source_modified_ns = None

        previous = self._data["files"].get(key, {})
        if not isinstance(previous, dict):
            previous = {}

        self._data["files"][key] = {
            **previous,
            "source_name": source_path.name,
            "source_path": str(source_path),
            "source_size": source_size,
            "source_modified_ns": source_modified_ns,
            "status": self.STATUS_ERROR,
            "error": str(error),
            "excluded": bool(previous.get("excluded", False)),
        }

        self.save()

    def get_error(
        self,
        source_file: Path | str,
    ) -> str:
        """Geef de laatst opgeslagen foutmelding terug."""

        entry = self._data["files"].get(
            self._source_key(Path(source_file))
        )

        if not isinstance(entry, dict):
            return ""

        return str(entry.get("error", "") or "")

    def set_excluded(
        self,
        source_file: Path | str,
        excluded: bool = True,
    ) -> None:
        """Markeer een bronbestand als uitgesloten of maak de uitsluiting ongedaan."""

        source_path = Path(source_file)
        key = self._source_key(source_path)

        previous = self._data["files"].get(key, {})
        if not isinstance(previous, dict):
            previous = {}

        try:
            stat = source_path.stat()
            source_size = stat.st_size
            source_modified_ns = stat.st_mtime_ns
        except OSError:
            source_size = previous.get("source_size")
            source_modified_ns = previous.get("source_modified_ns")

        self._data["files"][key] = {
            **previous,
            "source_name": source_path.name,
            "source_path": str(source_path),
            "source_size": source_size,
            "source_modified_ns": source_modified_ns,
            "excluded": bool(excluded),
        }

        self.save()

    def is_excluded(
        self,
        source_file: Path | str,
    ) -> bool:
        """Controleer of een bronbestand permanent uitgesloten is."""

        entry = self._data["files"].get(
            self._source_key(Path(source_file))
        )

        return bool(
            isinstance(entry, dict)
            and entry.get("excluded", False)
        )

    @staticmethod
    def _source_key(
        source_file: Path,
    ) -> str:
        """
        Bouw een stabiele sleutel voor een bronbestand.

        casefold() voorkomt dubbele registraties door hoofdletterverschillen
        op Windows.
        """

        try:
            resolved = source_file.resolve()

        except OSError:
            resolved = source_file.absolute()

        return str(
            resolved
        ).casefold()
