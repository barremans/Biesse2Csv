"""
================================================================================
Module:     app/gui/main_window.py
Project:    Biesse2Csv
Versie:     1.4.0
Datum:      2026-08-25
Auteur:     Bart Bossuyt

Doel:       Hoofdvenster van Biesse2Csv.
            Selecteert bron- en outputmappen, zoekt Biesse-machinebestanden,
            toont deze in een overzicht en converteert ze naar CSV en XLSX.
            Voorziet menubalk, taalkeuze en integratie met JSON-instellingen.
            Opent na conversie automatisch het eerste aangemaakte XLSX-bestand.

Wijzigingen:
  v1.0.0 (2026-08-24)  Initiële versie — QMainWindow met mapselectie,
                       bestandenoverzicht, conversie, statusbalk,
                       menubalk en runtime taalwissel.
  v1.1.0 (2026-08-24)  SettingsDialog gekoppeld aan menu Voorkeuren.
                       Gewijzigde taal, standaardmappen en conversie-
                       instellingen worden na sluiten direct toegepast.
  v1.1.1 (2026-08-24)  Ontbrekende _load_settings() hersteld en dubbele
                       tijdelijke open_settings() verwijderd.
  v1.2.0 (2026-08-24)  Automatisch openen van geconverteerd CSV-bestand
                       toegevoegd.
  v1.3.0 (2026-08-24)  Aangepast aan BiesseConverter v1.1.0. Conversie maakt
                       nu zowel CSV als XLSX. Het eerste succesvol aangemaakte
                       XLSX-bestand wordt automatisch geopend.
  v1.4.0 (2026-08-25)  Bevestigingsdialoog toegevoegd wanneer CSV/XLSX-output
                       reeds bestaat en automatisch overschrijven uit staat.
                       Gebruiker kan overschrijven, overslaan of annuleren.
                       Eindmelding toont nu ook het aantal overgeslagen bestanden.
================================================================================
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.gui.dialogs.settings_dialog import SettingsDialog
from helpers.biesse_converter import BiesseConverter


class MainWindow(QMainWindow):
    """Hoofdvenster van de Biesse2Csv-applicatie."""

    def __init__(
        self,
        settings_manager,
        translator,
    ) -> None:
        super().__init__()

        self.settings = settings_manager
        self.translator = translator

        self.source_files: list[Path] = []

        self._build_ui()
        self._build_menu()
        self._connect_signals()

        self._load_settings()
        self.retranslate_ui()
        self._scan_input_folder()

    # ==========================================================================
    # GUI
    # ==========================================================================

    def _build_ui(self) -> None:
        """Bouw de centrale gebruikersinterface."""

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # Bronmap
        # ----------------------------------------------------------------------

        self.input_label = QLabel()

        self.input_edit = QLineEdit()
        self.input_edit.setClearButtonEnabled(True)

        self.input_button = QPushButton()

        input_layout = QHBoxLayout()

        input_layout.addWidget(
            self.input_edit,
            1,
        )

        input_layout.addWidget(
            self.input_button,
        )

        # ----------------------------------------------------------------------
        # Outputmap
        # ----------------------------------------------------------------------

        self.output_label = QLabel()

        self.output_edit = QLineEdit()
        self.output_edit.setClearButtonEnabled(True)

        self.output_button = QPushButton()

        output_layout = QHBoxLayout()

        output_layout.addWidget(
            self.output_edit,
            1,
        )

        output_layout.addWidget(
            self.output_button,
        )

        # ----------------------------------------------------------------------
        # Bestanden
        # ----------------------------------------------------------------------

        self.files_found_label = QLabel()

        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)

        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.file_table.setAlternatingRowColors(True)

        self.file_table.verticalHeader().setVisible(
            False
        )

        header = self.file_table.horizontalHeader()

        header.setStretchLastSection(
            True
        )

        # ----------------------------------------------------------------------
        # Converteren
        # ----------------------------------------------------------------------

        self.convert_button = QPushButton()

        self.convert_button.setMinimumHeight(
            36
        )

        # ----------------------------------------------------------------------
        # Layout
        # ----------------------------------------------------------------------

        main_layout.addWidget(
            self.input_label
        )

        main_layout.addLayout(
            input_layout
        )

        main_layout.addSpacing(
            5
        )

        main_layout.addWidget(
            self.output_label
        )

        main_layout.addLayout(
            output_layout
        )

        main_layout.addSpacing(
            10
        )

        main_layout.addWidget(
            self.files_found_label
        )

        main_layout.addWidget(
            self.file_table,
            1,
        )

        main_layout.addSpacing(
            10
        )

        main_layout.addWidget(
            self.convert_button
        )

        self.setCentralWidget(
            central_widget
        )

        self.resize(
            900,
            550,
        )

        self.setMinimumSize(
            700,
            450,
        )

    # ==========================================================================
    # Menu
    # ==========================================================================

    def _build_menu(self) -> None:
        """Bouw de menubalk."""

        menu_bar = self.menuBar()

        # ----------------------------------------------------------------------
        # Bestand
        # ----------------------------------------------------------------------

        self.file_menu = menu_bar.addMenu("")

        self.exit_action = QAction(
            self
        )

        self.exit_action.setShortcut(
            QKeySequence.StandardKey.Quit
        )

        self.exit_action.triggered.connect(
            self.close
        )

        self.file_menu.addAction(
            self.exit_action
        )

        # ----------------------------------------------------------------------
        # Instellingen
        # ----------------------------------------------------------------------

        self.settings_menu = menu_bar.addMenu("")

        self.preferences_action = QAction(
            self
        )

        self.preferences_action.triggered.connect(
            self.open_settings
        )

        self.settings_menu.addAction(
            self.preferences_action
        )

        self.settings_menu.addSeparator()

        # ----------------------------------------------------------------------
        # Taal
        # ----------------------------------------------------------------------

        self.language_menu = self.settings_menu.addMenu("")

        self.language_action_group = QActionGroup(
            self
        )

        self.language_action_group.setExclusive(
            True
        )

        self.language_actions: dict[str, QAction] = {}

        for (
            language_code,
            language_name,
        ) in self.translator.available_languages().items():

            action = QAction(
                language_name,
                self,
            )

            action.setCheckable(
                True
            )

            action.setData(
                language_code
            )

            action.triggered.connect(
                self._language_action_triggered
            )

            self.language_action_group.addAction(
                action
            )

            self.language_menu.addAction(
                action
            )

            self.language_actions[
                language_code
            ] = action

        # ----------------------------------------------------------------------
        # Help
        # ----------------------------------------------------------------------

        self.help_menu = menu_bar.addMenu("")

        self.help_action = QAction(
            self
        )

        self.help_action.setShortcut(
            QKeySequence.StandardKey.HelpContents
        )

        self.help_action.triggered.connect(
            self.show_help
        )

        self.help_menu.addAction(
            self.help_action
        )

        self.about_action = QAction(
            self
        )

        self.about_action.triggered.connect(
            self.show_about
        )

        self.help_menu.addAction(
            self.about_action
        )

    # ==========================================================================
    # Signals
    # ==========================================================================

    def _connect_signals(self) -> None:
        """Verbind GUI-signalen met functies."""

        self.input_button.clicked.connect(
            self.select_input_folder
        )

        self.output_button.clicked.connect(
            self.select_output_folder
        )

        self.convert_button.clicked.connect(
            self.convert_files
        )

        self.input_edit.editingFinished.connect(
            self._input_folder_changed
        )

        self.output_edit.editingFinished.connect(
            self._output_folder_changed
        )

    # ==========================================================================
    # Instellingen
    # ==========================================================================

    def _load_settings(self) -> None:
        """Laad opgeslagen bron- en outputmappen."""

        input_folder = self.settings.get(
            "folders",
            "input_folder",
            "",
        )

        output_folder = self.settings.get(
            "folders",
            "output_folder",
            "",
        )

        self.input_edit.setText(
            input_folder
        )

        self.output_edit.setText(
            output_folder
        )

    def open_settings(self) -> None:
        """Open instellingenvenster en pas wijzigingen toe."""

        dialog = SettingsDialog(
            settings_manager=self.settings,
            translator=self.translator,
            parent=self,
        )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        language = self.settings.get(
            "general",
            "language",
            self.translator.DEFAULT_LANGUAGE,
        )

        self.translator.set_language(
            language
        )

        self._load_settings()

        self.retranslate_ui()

        self._scan_input_folder()

    def _save_folder_settings(self) -> None:
        """Bewaar bron- en outputmap."""

        self.settings.set(
            "folders",
            "input_folder",
            self.input_edit.text().strip(),
        )

        self.settings.set(
            "folders",
            "output_folder",
            self.output_edit.text().strip(),
        )

        self.settings.save()

    # ==========================================================================
    # Mapselectie
    # ==========================================================================

    def select_input_folder(self) -> None:
        """Open dialoog om de bronmap te kiezen."""

        start_folder = (
            self.input_edit.text().strip()
            or str(Path.home())
        )

        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.tr(
                "dialog.select_input_folder"
            ),
            start_folder,
        )

        if not folder:
            return

        self.input_edit.setText(
            folder
        )

        self._save_folder_settings()

        self._scan_input_folder()

    def select_output_folder(self) -> None:
        """Open dialoog om de outputmap te kiezen."""

        start_folder = (
            self.output_edit.text().strip()
            or str(Path.home())
        )

        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.tr(
                "dialog.select_output_folder"
            ),
            start_folder,
        )

        if not folder:
            return

        self.output_edit.setText(
            folder
        )

        self._save_folder_settings()

    def _input_folder_changed(self) -> None:
        """Verwerk handmatig gewijzigde bronmap."""

        self._save_folder_settings()

        self._scan_input_folder()

    def _output_folder_changed(self) -> None:
        """Verwerk handmatig gewijzigde outputmap."""

        self._save_folder_settings()

    # ==========================================================================
    # Bestanden zoeken
    # ==========================================================================

    def _scan_input_folder(self) -> None:
        """Zoek Biesse-bestanden in de bronmap."""

        self.source_files.clear()

        input_text = self.input_edit.text().strip()

        if not input_text:
            self._refresh_file_table()
            return

        input_folder = Path(
            input_text
        )

        if not input_folder.is_dir():
            self._refresh_file_table()
            return

        self.statusBar().showMessage(
            self.translator.tr(
                "main.status_scanning"
            )
        )

        for file_path in sorted(
            input_folder.iterdir()
        ):
            if not file_path.is_file():
                continue

            if BiesseConverter.is_biesse_file(
                file_path
            ):
                self.source_files.append(
                    file_path
                )

        self._refresh_file_table()

        self.statusBar().showMessage(
            self.translator.tr(
                "main.status_ready"
            )
        )

    def _refresh_file_table(self) -> None:
        """Werk bestandenoverzicht bij."""

        self.file_table.setRowCount(
            len(self.source_files)
        )

        for row, source_file in enumerate(
            self.source_files
        ):
            csv_name = BiesseConverter.build_output_name(
                source_file
            )

            xlsx_name = BiesseConverter.build_xlsx_output_name(
                source_file
            )

            filename_item = QTableWidgetItem(
                source_file.name
            )

            status_item = QTableWidgetItem(
                self.translator.tr(
                    "status.waiting"
                )
            )

            output_item = QTableWidgetItem(
                f"{csv_name} | {xlsx_name}"
            )

            self.file_table.setItem(
                row,
                0,
                filename_item,
            )

            self.file_table.setItem(
                row,
                1,
                status_item,
            )

            self.file_table.setItem(
                row,
                2,
                output_item,
            )

        self.files_found_label.setText(
            self.translator.tr(
                "main.files_found",
                count=len(self.source_files),
            )
        )

        self.convert_button.setEnabled(
            bool(self.source_files)
        )

    # ==========================================================================
    # Conversie
    # ==========================================================================

    def convert_files(self) -> None:
        """Converteer alle gevonden bestanden naar CSV en XLSX."""

        input_text = self.input_edit.text().strip()

        output_text = self.output_edit.text().strip()

        if not input_text:
            QMessageBox.warning(
                self,
                self.translator.tr(
                    "message.invalid_input_folder.title"
                ),
                self.translator.tr(
                    "message.invalid_input_folder.text"
                ),
            )
            return

        input_folder = Path(
            input_text
        )

        if not input_folder.is_dir():
            QMessageBox.warning(
                self,
                self.translator.tr(
                    "message.invalid_input_folder.title"
                ),
                self.translator.tr(
                    "message.invalid_input_folder.text"
                ),
            )
            return

        if not output_text:
            QMessageBox.warning(
                self,
                self.translator.tr(
                    "message.invalid_output_folder.title"
                ),
                self.translator.tr(
                    "message.invalid_output_folder.text"
                ),
            )
            return

        output_folder = Path(
            output_text
        )

        try:
            output_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

        except OSError:
            QMessageBox.warning(
                self,
                self.translator.tr(
                    "message.invalid_output_folder.title"
                ),
                self.translator.tr(
                    "message.invalid_output_folder.text"
                ),
            )
            return

        if not self.source_files:
            QMessageBox.information(
                self,
                self.translator.tr(
                    "message.no_files.title"
                ),
                self.translator.tr(
                    "message.no_files.text"
                ),
            )
            return

        overwrite = self.settings.get(
            "conversion",
            "overwrite_existing",
            False,
        )

        delimiter = self.settings.get(
            "conversion",
            "delimiter",
            ",",
        )

        encoding = self.settings.get(
            "conversion",
            "encoding",
            "utf-8-sig",
        )

        converter = BiesseConverter(
            delimiter=delimiter,
            encoding=encoding,
        )

        success_count = 0
        failed_count = 0
        skipped_count = 0

        converted_xlsx_files: list[Path] = []

        self.convert_button.setEnabled(
            False
        )

        self.statusBar().showMessage(
            self.translator.tr(
                "main.status_converting"
            )
        )

        for row, source_file in enumerate(
            self.source_files
        ):
            status_item = self.file_table.item(
                row,
                1,
            )

            if status_item is None:
                continue

            status_item.setText(
                self.translator.tr(
                    "status.processing"
                )
            )

            self.file_table.scrollToItem(
                status_item
            )

            QApplication.processEvents()

            csv_file = (
                output_folder
                / converter.build_output_name(
                    source_file
                )
            )

            xlsx_file = (
                output_folder
                / converter.build_xlsx_output_name(
                    source_file
                )
            )

            overwrite_this_file = bool(
                overwrite
            )

            if (
                not overwrite_this_file
                and (
                    csv_file.exists()
                    or xlsx_file.exists()
                )
            ):
                existing_files = [
                    path.name
                    for path in (
                        csv_file,
                        xlsx_file,
                    )
                    if path.exists()
                ]

                answer = self._ask_overwrite_existing(
                    existing_files
                )

                if (
                    answer
                    == QMessageBox.StandardButton.Cancel
                ):
                    status_item.setText(
                        self.translator.tr(
                            "status.skipped"
                        )
                    )

                    skipped_count += 1
                    break

                if (
                    answer
                    != QMessageBox.StandardButton.Yes
                ):
                    status_item.setText(
                        self.translator.tr(
                            "status.skipped"
                        )
                    )

                    skipped_count += 1
                    continue

                overwrite_this_file = True

            try:
                result = converter.convert_file(
                    source_file=source_file,
                    output_file=csv_file,
                    overwrite=overwrite_this_file,
                )

            except FileExistsError:
                status_item.setText(
                    self.translator.tr(
                        "status.skipped"
                    )
                )

                skipped_count += 1
                continue

            except Exception as exc:
                status_item.setText(
                    self.translator.tr(
                        "status.error"
                    )
                )

                status_item.setToolTip(
                    str(exc)
                )

                failed_count += 1

                continue

            status_item.setText(
                self.translator.tr(
                    "status.success"
                )
            )

            success_count += 1

            converted_xlsx_files.append(
                result.xlsx_file
            )

        self.convert_button.setEnabled(
            True
        )

        self.statusBar().showMessage(
            self.translator.tr(
                "main.status_finished"
            )
        )

        QMessageBox.information(
            self,
            self.translator.tr(
                "message.conversion_complete.title"
            ),
            self.translator.tr(
                "message.conversion_complete.text",
                success=success_count,
                failed=failed_count,
                skipped=skipped_count,
            ),
        )

        # ----------------------------------------------------------------------
        # Eerste succesvol aangemaakte XLSX openen
        # ----------------------------------------------------------------------

        if converted_xlsx_files:
            self._open_output_file(
                converted_xlsx_files[0]
            )

    def _ask_overwrite_existing(
        self,
        existing_files: list[str],
    ) -> QMessageBox.StandardButton:
        """
        Vraag wat er moet gebeuren wanneer outputbestanden reeds bestaan.

        Returns:
            QMessageBox.StandardButton.Yes:
                Bestaande output overschrijven.

            QMessageBox.StandardButton.No:
                Dit bronbestand overslaan.

            QMessageBox.StandardButton.Cancel:
                Verdere conversie stoppen.
        """

        filenames = "\n".join(
            f"• {filename}"
            for filename in existing_files
        )

        message = self.translator.tr(
            "message.overwrite.text",
            filenames=filenames,
        )

        return QMessageBox.question(
            self,
            self.translator.tr(
                "message.overwrite.title"
            ),
            message,
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )

    # ==========================================================================
    # Output openen
    # ==========================================================================

    def _open_output_file(
        self,
        file_path: Path,
    ) -> None:
        """
        Open outputbestand met de standaard Windows-applicatie.

        Voor XLSX zal dit normaal Microsoft Excel zijn wanneer Excel
        als standaardapplicatie gekoppeld is.
        """

        if not file_path.is_file():
            return

        try:
            os.startfile(
                str(file_path)
            )

        except OSError as exc:
            QMessageBox.warning(
                self,
                self.translator.tr(
                    "message.open_file_error.title",
                    default="Bestand openen mislukt",
                ),
                self.translator.tr(
                    "message.open_file_error.text",
                    default=(
                        "Het aangemaakte bestand kon niet automatisch "
                        f"worden geopend.\n\n{exc}"
                    ),
                ),
            )

    # ==========================================================================
    # Taal
    # ==========================================================================

    def _language_action_triggered(
        self,
        checked: bool,
    ) -> None:
        """Verwerk taalkeuze vanuit menu."""

        if not checked:
            return

        action = self.sender()

        if not isinstance(
            action,
            QAction,
        ):
            return

        language_code = action.data()

        if not language_code:
            return

        if not self.translator.set_language(
            language_code
        ):
            return

        self.settings.set(
            "general",
            "language",
            language_code,
            save=True,
        )

        self.retranslate_ui()

    # ==========================================================================
    # Vertaling
    # ==========================================================================

    def retranslate_ui(self) -> None:
        """Werk alle zichtbare GUI-teksten bij."""

        tr = self.translator.tr

        self.setWindowTitle(
            tr("app.title")
        )

        # ----------------------------------------------------------------------
        # Menu
        # ----------------------------------------------------------------------

        self.file_menu.setTitle(
            tr("menu.file")
        )

        self.settings_menu.setTitle(
            tr("menu.settings")
        )

        self.language_menu.setTitle(
            tr("menu.language")
        )

        self.help_menu.setTitle(
            tr("menu.help")
        )

        self.exit_action.setText(
            tr("menu.exit")
        )

        self.preferences_action.setText(
            tr("menu.preferences")
        )

        self.help_action.setText(
            tr("menu.help_contents")
        )

        self.about_action.setText(
            tr("menu.about")
        )

        # ----------------------------------------------------------------------
        # Centrale GUI
        # ----------------------------------------------------------------------

        self.input_label.setText(
            tr("main.input_folder")
        )

        self.output_label.setText(
            tr("main.output_folder")
        )

        self.input_edit.setPlaceholderText(
            tr("main.input_placeholder")
        )

        self.output_edit.setPlaceholderText(
            tr("main.output_placeholder")
        )

        self.input_button.setText(
            tr("main.browse")
        )

        self.output_button.setText(
            tr("main.browse")
        )

        self.convert_button.setText(
            tr("main.convert")
        )

        # ----------------------------------------------------------------------
        # Tabel
        # ----------------------------------------------------------------------

        self.file_table.setHorizontalHeaderLabels(
            [
                tr("main.table.filename"),
                tr("main.table.status"),
                tr("main.table.output"),
            ]
        )

        self.file_table.setColumnWidth(
            0,
            220,
        )

        self.file_table.setColumnWidth(
            1,
            120,
        )

        # ----------------------------------------------------------------------
        # Taalmarkering
        # ----------------------------------------------------------------------

        current_language = (
            self.translator.current_language()
        )

        for (
            language_code,
            action,
        ) in self.language_actions.items():

            action.setChecked(
                language_code
                == current_language
            )

        self._refresh_file_table()

        self.statusBar().showMessage(
            tr("main.status_ready")
        )

    # ==========================================================================
    # Help
    # ==========================================================================

    def show_help(self) -> None:
        """Toon voorlopig een eenvoudige helpmelding."""

        QMessageBox.information(
            self,
            self.translator.tr(
                "menu.help_contents"
            ),
            self.translator.tr(
                "about.text"
            ),
        )

    def show_about(self) -> None:
        """Toon informatie over Biesse2Csv."""

        QMessageBox.about(
            self,
            self.translator.tr(
                "about.title"
            ),
            self.translator.tr(
                "about.text"
            ),
        )

    # ==========================================================================
    # Venster sluiten
    # ==========================================================================

    def closeEvent(
        self,
        event,
    ) -> None:
        """Bewaar huidige mappen wanneer applicatie sluit."""

        self._save_folder_settings()

        event.accept()