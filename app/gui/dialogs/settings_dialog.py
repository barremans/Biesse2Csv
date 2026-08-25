"""
================================================================================
Module:     app/gui/dialogs/settings_dialog.py
Project:    Biesse2Csv
Versie:     1.0.0
Datum:      2026-08-24
Auteur:     Bart Bossuyt

Doel:       Instellingenvenster voor Biesse2Csv.
            Beheert standaard bron- en outputmappen, taalkeuze en
            conversie-instellingen via de centrale SettingsManager.

Wijzigingen:
  v1.0.0 (2026-08-24)  Initiële versie — instellingenvenster met taalkeuze,
                       standaardmappen, CSV-instellingen en resetfunctie.
================================================================================
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    """Dialoogvenster voor de applicatie-instellingen."""

    def __init__(
        self,
        settings_manager,
        translator,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.settings = settings_manager
        self.translator = translator

        self._build_ui()
        self._connect_signals()
        self._load_settings()
        self.retranslate_ui()

    # ==========================================================================
    # GUI
    # ==========================================================================

    def _build_ui(self) -> None:
        """Bouw de volledige instellingeninterface."""

        self.setModal(True)

        self.resize(
            650,
            420,
        )

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(15)

        # ----------------------------------------------------------------------
        # Algemeen
        # ----------------------------------------------------------------------

        self.general_group = QGroupBox()

        general_layout = QFormLayout(
            self.general_group
        )

        self.language_label = QLabel()

        self.language_combo = QComboBox()

        general_layout.addRow(
            self.language_label,
            self.language_combo,
        )

        # ----------------------------------------------------------------------
        # Mappen
        # ----------------------------------------------------------------------

        self.folders_group = QGroupBox()

        folders_layout = QFormLayout(
            self.folders_group
        )

        # Standaard bronmap
        self.input_folder_label = QLabel()

        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setClearButtonEnabled(
            True
        )

        self.input_folder_button = QPushButton()

        input_folder_widget = QWidget()

        input_folder_layout = QHBoxLayout(
            input_folder_widget
        )

        input_folder_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        input_folder_layout.addWidget(
            self.input_folder_edit,
            1,
        )

        input_folder_layout.addWidget(
            self.input_folder_button
        )

        folders_layout.addRow(
            self.input_folder_label,
            input_folder_widget,
        )

        # Standaard outputmap
        self.output_folder_label = QLabel()

        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setClearButtonEnabled(
            True
        )

        self.output_folder_button = QPushButton()

        output_folder_widget = QWidget()

        output_folder_layout = QHBoxLayout(
            output_folder_widget
        )

        output_folder_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        output_folder_layout.addWidget(
            self.output_folder_edit,
            1,
        )

        output_folder_layout.addWidget(
            self.output_folder_button
        )

        folders_layout.addRow(
            self.output_folder_label,
            output_folder_widget,
        )

        # ----------------------------------------------------------------------
        # Conversie
        # ----------------------------------------------------------------------

        self.conversion_group = QGroupBox()

        conversion_layout = QFormLayout(
            self.conversion_group
        )

        self.delimiter_label = QLabel()

        self.delimiter_combo = QComboBox()

        self.delimiter_combo.addItem(
            ";",
            ";",
        )

        self.delimiter_combo.addItem(
            ",",
            ",",
        )

        self.delimiter_combo.addItem(
            "Tab",
            "\t",
        )

        conversion_layout.addRow(
            self.delimiter_label,
            self.delimiter_combo,
        )

        self.encoding_label = QLabel()

        self.encoding_combo = QComboBox()

        self.encoding_combo.addItem(
            "UTF-8 BOM",
            "utf-8-sig",
        )

        self.encoding_combo.addItem(
            "UTF-8",
            "utf-8",
        )

        self.encoding_combo.addItem(
            "Windows-1252",
            "cp1252",
        )

        conversion_layout.addRow(
            self.encoding_label,
            self.encoding_combo,
        )

        self.overwrite_checkbox = QCheckBox()

        conversion_layout.addRow(
            "",
            self.overwrite_checkbox,
        )

        # ----------------------------------------------------------------------
        # Resetknop
        # ----------------------------------------------------------------------

        self.reset_button = QPushButton()

        # ----------------------------------------------------------------------
        # Dialoogknoppen
        # ----------------------------------------------------------------------

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        # ----------------------------------------------------------------------
        # Hoofd-layout
        # ----------------------------------------------------------------------

        main_layout.addWidget(
            self.general_group
        )

        main_layout.addWidget(
            self.folders_group
        )

        main_layout.addWidget(
            self.conversion_group
        )

        main_layout.addStretch()

        bottom_layout = QHBoxLayout()

        bottom_layout.addWidget(
            self.reset_button
        )

        bottom_layout.addStretch()

        bottom_layout.addWidget(
            self.button_box
        )

        main_layout.addLayout(
            bottom_layout
        )

    # ==========================================================================
    # Signals
    # ==========================================================================

    def _connect_signals(self) -> None:
        """Verbind widgets met hun functies."""

        self.input_folder_button.clicked.connect(
            self.select_input_folder
        )

        self.output_folder_button.clicked.connect(
            self.select_output_folder
        )

        self.reset_button.clicked.connect(
            self.reset_settings
        )

        self.button_box.accepted.connect(
            self.save_settings
        )

        self.button_box.rejected.connect(
            self.reject
        )

    # ==========================================================================
    # Instellingen laden
    # ==========================================================================

    def _load_settings(self) -> None:
        """Laad de huidige instellingen in de widgets."""

        self._load_languages()

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

        delimiter = self.settings.get(
            "conversion",
            "delimiter",
            ";",
        )

        encoding = self.settings.get(
            "conversion",
            "encoding",
            "utf-8-sig",
        )

        overwrite = self.settings.get(
            "conversion",
            "overwrite_existing",
            False,
        )

        self.input_folder_edit.setText(
            input_folder
        )

        self.output_folder_edit.setText(
            output_folder
        )

        self._select_combo_by_data(
            self.delimiter_combo,
            delimiter,
        )

        self._select_combo_by_data(
            self.encoding_combo,
            encoding,
        )

        self.overwrite_checkbox.setChecked(
            bool(overwrite)
        )

    def _load_languages(self) -> None:
        """Vul de taalkeuzelijst."""

        self.language_combo.clear()

        current_language = self.settings.get(
            "general",
            "language",
            self.translator.DEFAULT_LANGUAGE,
        )

        for (
            language_code,
            language_name,
        ) in self.translator.available_languages().items():

            self.language_combo.addItem(
                language_name,
                language_code,
            )

        self._select_combo_by_data(
            self.language_combo,
            current_language,
        )

    # ==========================================================================
    # Hulpfuncties
    # ==========================================================================

    @staticmethod
    def _select_combo_by_data(
        combo: QComboBox,
        value,
    ) -> None:
        """
        Selecteer een QComboBox-item op basis van userData.
        """

        index = combo.findData(
            value
        )

        if index >= 0:
            combo.setCurrentIndex(
                index
            )

    # ==========================================================================
    # Mapselectie
    # ==========================================================================

    def select_input_folder(self) -> None:
        """Selecteer de standaard bronmap."""

        current_folder = (
            self.input_folder_edit.text().strip()
            or str(Path.home())
        )

        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.tr(
                "dialog.select_input_folder"
            ),
            current_folder,
        )

        if folder:
            self.input_folder_edit.setText(
                folder
            )

    def select_output_folder(self) -> None:
        """Selecteer de standaard outputmap."""

        current_folder = (
            self.output_folder_edit.text().strip()
            or str(Path.home())
        )

        folder = QFileDialog.getExistingDirectory(
            self,
            self.translator.tr(
                "dialog.select_output_folder"
            ),
            current_folder,
        )

        if folder:
            self.output_folder_edit.setText(
                folder
            )

    # ==========================================================================
    # Opslaan
    # ==========================================================================

    def save_settings(self) -> None:
        """Bewaar alle instellingen."""

        language = self.language_combo.currentData()

        input_folder = (
            self.input_folder_edit.text().strip()
        )

        output_folder = (
            self.output_folder_edit.text().strip()
        )

        delimiter = (
            self.delimiter_combo.currentData()
        )

        encoding = (
            self.encoding_combo.currentData()
        )

        overwrite = (
            self.overwrite_checkbox.isChecked()
        )

        self.settings.set(
            "general",
            "language",
            language,
        )

        self.settings.set(
            "folders",
            "input_folder",
            input_folder,
        )

        self.settings.set(
            "folders",
            "output_folder",
            output_folder,
        )

        self.settings.set(
            "conversion",
            "delimiter",
            delimiter,
        )

        self.settings.set(
            "conversion",
            "encoding",
            encoding,
        )

        self.settings.set(
            "conversion",
            "overwrite_existing",
            overwrite,
        )

        self.settings.save()

        self.translator.set_language(
            language
        )

        self.accept()

    # ==========================================================================
    # Reset
    # ==========================================================================

    def reset_settings(self) -> None:
        """Vraag bevestiging en herstel standaardinstellingen."""

        result = QMessageBox.question(
            self,
            self.translator.tr(
                "message.reset_settings.title"
            ),
            self.translator.tr(
                "message.reset_settings.text"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            result
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.settings.reset()

        default_language = self.settings.get(
            "general",
            "language",
            self.translator.DEFAULT_LANGUAGE,
        )

        self.translator.set_language(
            default_language
        )

        self._load_settings()
        self.retranslate_ui()

    # ==========================================================================
    # Vertaling
    # ==========================================================================

    def retranslate_ui(self) -> None:
        """Werk alle zichtbare teksten bij."""

        tr = self.translator.tr

        self.setWindowTitle(
            tr("settings.title")
        )

        # Groepen
        self.general_group.setTitle(
            tr("settings.general")
        )

        self.folders_group.setTitle(
            tr("settings.folders")
        )

        self.conversion_group.setTitle(
            tr("settings.conversion")
        )

        # Algemeen
        self.language_label.setText(
            tr("settings.language")
        )

        # Mappen
        self.input_folder_label.setText(
            tr("settings.default_input_folder")
        )

        self.output_folder_label.setText(
            tr("settings.default_output_folder")
        )

        self.input_folder_button.setText(
            tr("main.browse")
        )

        self.output_folder_button.setText(
            tr("main.browse")
        )

        # Conversie
        self.delimiter_label.setText(
            tr("settings.delimiter")
        )

        self.encoding_label.setText(
            tr("settings.encoding")
        )

        self.overwrite_checkbox.setText(
            tr("settings.overwrite_existing")
        )

        # Reset
        self.reset_button.setText(
            tr("settings.reset")
        )

        # Standaard Qt-knoppen hernoemen via onze translator.
        save_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Save
        )

        cancel_button = self.button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        if save_button:
            save_button.setText(
                tr("settings.save")
            )

        if cancel_button:
            cancel_button.setText(
                tr("settings.cancel")
            )