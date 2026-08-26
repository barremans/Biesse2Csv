"""
================================================================================
Module:     app/gui/main_window.py
Project:    Biesse2Csv
Versie:     1.7.0
Datum:      2026-08-26
Auteur:     Bart Bossuyt

Doel:       Hoofdvenster van Biesse2Csv.
            Selecteert bron- en outputmappen, zoekt Biesse-machinebestanden,
            toont deze in een overzicht en converteert ze naar CSV en XLSX.
            Voorziet menubalk, taalkeuze en integratie met JSON-instellingen.
            Opent na conversie automatisch het eerste aangemaakte XLSX-bestand.

Wijzigingen:
  v1.7.0 (2026-08-26)  Foutredenen worden permanent opgeslagen en zijn via
                       tooltip/Foutdetails zichtbaar. Bestanden kunnen
                       permanent uitgesloten worden en zijn standaard verborgen.
                       Filters toegevoegd voor bestandsnaam en status.
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
  v1.5.0 (2026-08-26)  Selecteerbare bestanden toegevoegd. Alleen aangevinkte
                       bestanden worden geconverteerd. Knoppen toegevoegd voor
                       alles selecteren, selectie wissen en niet-verwerkte
                       bestanden selecteren. Permanente conversiehistoriek
                       geïntegreerd met status voor verwerkt/gewijzigd.
  v1.6.0 (2026-08-26)  Overwrite-workflow uitgebreid met 'Ja op alles'.
                       Niet-verwerkte bestanden krijgen voorrang en mogen
                       bestaande output zonder bevestiging overschrijven.
                       'Ja op alles' geldt voor de resterende huidige batch.
================================================================================
"""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
from helpers.conversion_history import ConversionHistory


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
        self.conversion_history = ConversionHistory()

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
        self.file_table.setColumnCount(5)

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
        # Filters
        # ----------------------------------------------------------------------

        self.filter_label = QLabel()
        self.filter_edit = QLineEdit()
        self.filter_edit.setClearButtonEnabled(True)

        self.status_filter = QComboBox()

        self.show_excluded_checkbox = QCheckBox()
        self.show_excluded_checkbox.setChecked(False)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_edit, 1)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(self.show_excluded_checkbox)

        # ----------------------------------------------------------------------
        # Selectieknoppen
        # ----------------------------------------------------------------------

        self.select_all_button = QPushButton()
        self.clear_selection_button = QPushButton()
        self.select_unprocessed_button = QPushButton()
        self.exclude_selected_button = QPushButton()
        self.restore_excluded_button = QPushButton()
        self.error_details_button = QPushButton()

        selection_layout = QHBoxLayout()
        selection_layout.addWidget(self.select_all_button)
        selection_layout.addWidget(self.clear_selection_button)
        selection_layout.addWidget(self.select_unprocessed_button)
        selection_layout.addWidget(self.exclude_selected_button)
        selection_layout.addWidget(self.restore_excluded_button)
        selection_layout.addWidget(self.error_details_button)
        selection_layout.addStretch(1)

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

        main_layout.addLayout(
            filter_layout
        )

        main_layout.addWidget(
            self.file_table,
            1,
        )

        main_layout.addLayout(
            selection_layout
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

        self.select_all_button.clicked.connect(
            self.select_all_files
        )

        self.clear_selection_button.clicked.connect(
            self.clear_file_selection
        )

        self.select_unprocessed_button.clicked.connect(
            self.select_unprocessed_files
        )

        self.exclude_selected_button.clicked.connect(
            self.exclude_selected_files
        )

        self.restore_excluded_button.clicked.connect(
            self.restore_excluded_files
        )

        self.error_details_button.clicked.connect(
            self.show_selected_error_details
        )

        self.filter_edit.textChanged.connect(
            self._apply_table_filters
        )

        self.status_filter.currentIndexChanged.connect(
            self._apply_table_filters
        )

        self.show_excluded_checkbox.toggled.connect(
            self._apply_table_filters
        )

        self.file_table.itemDoubleClicked.connect(
            self._table_item_double_clicked
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

            select_item = QTableWidgetItem()
            select_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            select_item.setCheckState(
                Qt.CheckState.Unchecked
            )

            filename_item = QTableWidgetItem(
                source_file.name
            )

            history_status = self.conversion_history.get_status(
                source_file
            )

            status_item = QTableWidgetItem(
                self._history_status_text(
                    history_status
                )
            )

            error_text = self.conversion_history.get_error(
                source_file
            )

            if error_text:
                status_item.setToolTip(
                    error_text
                )

            processed_item = QTableWidgetItem(
                self.conversion_history.get_processed_at(
                    source_file
                )
                or "—"
            )

            output_item = QTableWidgetItem(
                f"{csv_name} | {xlsx_name}"
            )

            self.file_table.setItem(
                row,
                0,
                select_item,
            )

            self.file_table.setItem(
                row,
                1,
                filename_item,
            )

            self.file_table.setItem(
                row,
                2,
                status_item,
            )

            self.file_table.setItem(
                row,
                3,
                processed_item,
            )

            self.file_table.setItem(
                row,
                4,
                output_item,
            )

        self.files_found_label.setText(
            self.translator.tr(
                "main.files_found",
                count=len(self.source_files),
            )
        )

        has_files = bool(
            self.source_files
        )

        self.convert_button.setEnabled(
            has_files
        )

        self.select_all_button.setEnabled(
            has_files
        )

        self.clear_selection_button.setEnabled(
            has_files
        )

        self.select_unprocessed_button.setEnabled(
            has_files
        )

        self.exclude_selected_button.setEnabled(
            has_files
        )

        self.restore_excluded_button.setEnabled(
            has_files
        )

        self.error_details_button.setEnabled(
            has_files
        )

        self._apply_table_filters()

    def _history_status_text(
        self,
        history_status: str,
    ) -> str:
        """Vertaal een interne historiekstatus naar zichtbare tekst."""

        status_keys = {
            ConversionHistory.STATUS_NOT_PROCESSED:
                "status.not_processed",
            ConversionHistory.STATUS_PROCESSED:
                "status.processed",
            ConversionHistory.STATUS_MODIFIED:
                "status.modified",
            ConversionHistory.STATUS_ERROR:
                "status.error",
            ConversionHistory.STATUS_EXCLUDED:
                "status.excluded",
        }

        return self.translator.tr(
            status_keys.get(
                history_status,
                "status.not_processed",
            )
        )

    def _selected_source_rows(
        self,
    ) -> list[tuple[int, Path]]:
        """Geef alleen de aangevinkte bronbestanden met hun tabelrij terug."""

        selected: list[tuple[int, Path]] = []

        for row, source_file in enumerate(
            self.source_files
        ):
            select_item = self.file_table.item(
                row,
                0,
            )

            if (
                not self.file_table.isRowHidden(row)
                and select_item is not None
                and select_item.checkState()
                == Qt.CheckState.Checked
            ):
                selected.append(
                    (row, source_file)
                )

        return selected

    def select_all_files(self) -> None:
        """Vink alle gevonden bestanden aan."""

        for row in range(
            self.file_table.rowCount()
        ):
            item = self.file_table.item(
                row,
                0,
            )

            if (
                item is not None
                and not self.file_table.isRowHidden(row)
            ):
                item.setCheckState(
                    Qt.CheckState.Checked
                )

    def clear_file_selection(self) -> None:
        """Wis alle bestandsselecties."""

        for row in range(
            self.file_table.rowCount()
        ):
            item = self.file_table.item(
                row,
                0,
            )

            if item is not None:
                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

    def select_unprocessed_files(self) -> None:
        """Vink bestanden aan die nog niet verwerkt of later gewijzigd zijn."""

        for row, source_file in enumerate(
            self.source_files
        ):
            item = self.file_table.item(
                row,
                0,
            )

            if item is None:
                continue

            history_status = self.conversion_history.get_status(
                source_file
            )

            should_select = history_status in {
                ConversionHistory.STATUS_NOT_PROCESSED,
                ConversionHistory.STATUS_MODIFIED,
            }

            item.setCheckState(
                Qt.CheckState.Checked
                if should_select
                else Qt.CheckState.Unchecked
            )

    def _apply_table_filters(self) -> None:
        """Pas bestandsnaam-, status- en uitsluitingsfilters toe."""

        search_text = self.filter_edit.text().strip().casefold()
        status_value = self.status_filter.currentData()
        show_excluded = self.show_excluded_checkbox.isChecked()

        for row, source_file in enumerate(self.source_files):
            history_status = self.conversion_history.get_status(
                source_file
            )

            filename_match = (
                not search_text
                or search_text in source_file.name.casefold()
            )

            status_match = (
                not status_value
                or history_status == status_value
            )

            excluded_match = (
                show_excluded
                or history_status != ConversionHistory.STATUS_EXCLUDED
            )

            self.file_table.setRowHidden(
                row,
                not (
                    filename_match
                    and status_match
                    and excluded_match
                ),
            )

    def exclude_selected_files(self) -> None:
        """Sluit geselecteerde bestanden permanent uit van het standaardoverzicht."""

        selected = self._selected_source_rows()

        for _row, source_file in selected:
            self.conversion_history.set_excluded(
                source_file,
                True,
            )

        self._refresh_file_table()
        self._apply_table_filters()

    def restore_excluded_files(self) -> None:
        """Maak uitsluiting ongedaan voor aangevinkte zichtbare bestanden."""

        for row, source_file in enumerate(self.source_files):
            item = self.file_table.item(row, 0)

            if (
                item is not None
                and item.checkState() == Qt.CheckState.Checked
            ):
                self.conversion_history.set_excluded(
                    source_file,
                    False,
                )

        self._refresh_file_table()
        self._apply_table_filters()

    def show_selected_error_details(self) -> None:
        """Toon de foutreden van het eerste geselecteerde foutbestand."""

        selected = self._selected_source_rows()

        if not selected:
            QMessageBox.information(
                self,
                self.translator.tr("message.no_selection.title"),
                self.translator.tr("message.no_selection.text"),
            )
            return

        _row, source_file = selected[0]
        error_text = self.conversion_history.get_error(
            source_file
        )

        if not error_text:
            QMessageBox.information(
                self,
                self.translator.tr("message.error_details.title"),
                self.translator.tr("message.error_details.none"),
            )
            return

        QMessageBox.information(
            self,
            self.translator.tr("message.error_details.title"),
            self.translator.tr(
                "message.error_details.text",
                filename=source_file.name,
                error=error_text,
            ),
        )

    def _table_item_double_clicked(
        self,
        item: QTableWidgetItem,
    ) -> None:
        """Toon bij dubbelklik op een foutstatus direct de foutdetails."""

        row = item.row()

        if not (0 <= row < len(self.source_files)):
            return

        source_file = self.source_files[row]
        error_text = self.conversion_history.get_error(
            source_file
        )

        if not error_text:
            return

        QMessageBox.information(
            self,
            self.translator.tr("message.error_details.title"),
            self.translator.tr(
                "message.error_details.text",
                filename=source_file.name,
                error=error_text,
            ),
        )

    # ==========================================================================
    # Conversie
    # ==========================================================================

    def convert_files(self) -> None:
        """Converteer uitsluitend de door de gebruiker geselecteerde bestanden."""

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

        selected_files = self._selected_source_rows()

        if not selected_files:
            QMessageBox.information(
                self,
                self.translator.tr(
                    "message.no_selection.title"
                ),
                self.translator.tr(
                    "message.no_selection.text"
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
        overwrite_all_remaining = False

        converted_xlsx_files: list[Path] = []

        self.convert_button.setEnabled(
            False
        )

        self.statusBar().showMessage(
            self.translator.tr(
                "main.status_converting"
            )
        )

        for row, source_file in selected_files:
            status_item = self.file_table.item(
                row,
                2,
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

            history_status = self.conversion_history.get_status(
                source_file
            )

            # Nog niet verwerkt heeft voorrang op reeds aanwezige output:
            # deze output mag zonder vraag worden vervangen.
            overwrite_this_file = bool(
                overwrite
                or overwrite_all_remaining
                or history_status
                == ConversionHistory.STATUS_NOT_PROCESSED
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

                if answer == "cancel":
                    status_item.setText(
                        self.translator.tr(
                            "status.skipped"
                        )
                    )
                    skipped_count += 1
                    break

                if answer == "no":
                    status_item.setText(
                        self.translator.tr(
                            "status.skipped"
                        )
                    )
                    skipped_count += 1
                    continue

                if answer == "yes_to_all":
                    overwrite_all_remaining = True

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
                error_text = str(exc)

                status_item.setText(
                    self.translator.tr(
                        "status.error"
                    )
                )

                status_item.setToolTip(
                    error_text
                )

                self.conversion_history.mark_error(
                    source_file=source_file,
                    error=error_text,
                )

                failed_count += 1

                continue

            status_item.setText(
                self.translator.tr(
                    "status.processed"
                )
            )

            success_count += 1

            self.conversion_history.mark_success(
                source_file=source_file,
                csv_file=result.csv_file,
                xlsx_file=result.xlsx_file,
            )

            processed_item = self.file_table.item(
                row,
                3,
            )

            if processed_item is not None:
                processed_item.setText(
                    self.conversion_history.get_processed_at(
                        source_file
                    )
                )

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
    ) -> str:
        """
        Vraag wat er moet gebeuren wanneer outputbestanden reeds bestaan.

        Returns:
            "yes":
                Alleen dit bronbestand overschrijven.

            "yes_to_all":
                Dit en alle volgende conflicten in de huidige batch
                overschrijven.

            "no":
                Dit bronbestand overslaan.

            "cancel":
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

        dialog = QMessageBox(
            QMessageBox.Icon.Question,
            self.translator.tr(
                "message.overwrite.title"
            ),
            message,
            parent=self,
        )

        yes_button = dialog.addButton(
            self.translator.tr(
                "button.yes"
            ),
            QMessageBox.ButtonRole.YesRole,
        )

        yes_to_all_button = dialog.addButton(
            self.translator.tr(
                "button.yes_to_all",
                default="Ja op alles",
            ),
            QMessageBox.ButtonRole.YesRole,
        )

        no_button = dialog.addButton(
            self.translator.tr(
                "button.no"
            ),
            QMessageBox.ButtonRole.NoRole,
        )

        cancel_button = dialog.addButton(
            self.translator.tr(
                "button.cancel"
            ),
            QMessageBox.ButtonRole.RejectRole,
        )

        dialog.setDefaultButton(
            no_button
        )

        dialog.exec()

        clicked_button = dialog.clickedButton()

        if clicked_button is yes_button:
            return "yes"

        if clicked_button is yes_to_all_button:
            return "yes_to_all"

        if clicked_button is no_button:
            return "no"

        if clicked_button is cancel_button:
            return "cancel"

        return "cancel"

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

        self.select_all_button.setText(
            tr("main.select_all")
        )

        self.clear_selection_button.setText(
            tr("main.clear_selection")
        )

        self.select_unprocessed_button.setText(
            tr("main.select_unprocessed")
        )

        self.exclude_selected_button.setText(
            tr("main.exclude_selected")
        )

        self.restore_excluded_button.setText(
            tr("main.restore_excluded")
        )

        self.error_details_button.setText(
            tr("main.error_details")
        )

        self.filter_label.setText(
            tr("main.filter")
        )

        self.filter_edit.setPlaceholderText(
            tr("main.filter_placeholder")
        )

        self.show_excluded_checkbox.setText(
            tr("main.show_excluded")
        )

        current_status_filter = self.status_filter.currentData()

        self.status_filter.blockSignals(True)
        self.status_filter.clear()
        self.status_filter.addItem(
            tr("filter.all_statuses"),
            None,
        )
        self.status_filter.addItem(
            tr("status.not_processed"),
            ConversionHistory.STATUS_NOT_PROCESSED,
        )
        self.status_filter.addItem(
            tr("status.processed"),
            ConversionHistory.STATUS_PROCESSED,
        )
        self.status_filter.addItem(
            tr("status.modified"),
            ConversionHistory.STATUS_MODIFIED,
        )
        self.status_filter.addItem(
            tr("status.error"),
            ConversionHistory.STATUS_ERROR,
        )
        self.status_filter.addItem(
            tr("status.excluded"),
            ConversionHistory.STATUS_EXCLUDED,
        )

        if current_status_filter is not None:
            index = self.status_filter.findData(
                current_status_filter
            )
            if index >= 0:
                self.status_filter.setCurrentIndex(
                    index
                )

        self.status_filter.blockSignals(False)

        # ----------------------------------------------------------------------
        # Tabel
        # ----------------------------------------------------------------------

        self.file_table.setHorizontalHeaderLabels(
            [
                tr("main.table.select"),
                tr("main.table.filename"),
                tr("main.table.status"),
                tr("main.table.processed_at"),
                tr("main.table.output"),
            ]
        )

        self.file_table.setColumnWidth(
            0,
            70,
        )

        self.file_table.setColumnWidth(
            1,
            220,
        )

        self.file_table.setColumnWidth(
            2,
            180,
        )

        self.file_table.setColumnWidth(
            3,
            155,
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