import base64
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
                             QLabel, QSpinBox, QDialogButtonBox, QSizePolicy)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
try:
    from translations import tr as app_tr
except ImportError:
    print("Warning: translations.py not found. Using basic fallback for SettingsDialog.")

    def app_tr(text, lang='en', *args, **kwargs):
        try:
            return text.format(*args, **kwargs)
        except (KeyError, IndexError):
            return text
try:
    from flag_icons import FLAG_ICONS
except ImportError:
    print("Warning: flag_icons.py not found. Language flags will be missing in SettingsDialog.")
    FLAG_ICONS = {}

class SettingsDialog(QDialog):
    """
    A dialog window for configuring application settings like language
    and maximum displayed name length.
    """

    def __init__(self, current_language, current_max_length, min_len, max_len, parent=None, tr_func=None):
        """
        Initializes the Settings Dialog.
        Args:
            current_language (str): The currently active language code (e.g., 'en', 'ru').
            current_max_length (int): The currently set maximum name length.
            min_len (int): The minimum allowed value for maximum name length.
            max_len (int): The maximum allowed value for maximum name length.
            parent (QWidget, optional): The parent widget. Defaults to None.
            tr_func (callable, optional): The translation function to use.
                                          Defaults to the fallback or imported app_tr.
        """
        super().__init__(parent)
        self.tr = tr_func if callable(tr_func) else app_tr
        self.current_language = current_language
        self.setWindowTitle(self.tr("Settings", self.current_language))
        self.setMinimumWidth(350)
        main_layout = QVBoxLayout(self)
        lang_group_box = QGroupBox(self.tr("Language:", self.current_language))
        lang_layout = QHBoxLayout()
        self.radio_en = QRadioButton("English")
        self.radio_ru = QRadioButton("Русский")
        self.radio_zh = QRadioButton("中文")
        self._setup_language_radio(self.radio_en, 'en', FLAG_ICONS.get('en'))
        self._setup_language_radio(self.radio_ru, 'ru', FLAG_ICONS.get('ru'))
        self._setup_language_radio(self.radio_zh, 'zh', FLAG_ICONS.get('zh'))
        lang_layout.addWidget(self.radio_en)
        lang_layout.addWidget(self.radio_ru)
        lang_layout.addWidget(self.radio_zh)
        lang_layout.addStretch()
        lang_group_box.setLayout(lang_layout)
        main_layout.addWidget(lang_group_box)
        if current_language == 'en':
            self.radio_en.setChecked(True)
        elif current_language == 'ru':
            self.radio_ru.setChecked(True)
        elif current_language == 'zh':
            self.radio_zh.setChecked(True)
        else:
            self.radio_en.setChecked(True)
        length_layout = QHBoxLayout()
        length_label = QLabel(self.tr("Maximum Name Length (UI):", self.current_language))
        self.spin_max_length = QSpinBox()
        self.spin_max_length.setRange(min_len, max_len)
        clamped_current_max_length = max(min_len, min(max_len, current_max_length))
        self.spin_max_length.setValue(clamped_current_max_length)
        tooltip_template = self.tr("Limits the displayed name length in the UI ({min}-{max}).", self.current_language)
        tooltip_text = tooltip_template.format(min=min_len, max=max_len)
        self.spin_max_length.setToolTip(tooltip_text)
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.spin_max_length)
        main_layout.addLayout(length_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def _setup_language_radio(self, radio_button, lang_code, base64_icon):
        """
        Configures the appearance and properties of a language radio button.
        Args:
            radio_button (QRadioButton): The radio button widget to configure.
            lang_code (str): The language code associated with this button (e.g., 'en').
            base64_icon (str | None): Base64 encoded string for the flag icon, or None.
        """
        radio_button.setProperty("language_code", lang_code)
        radio_button.setText("")
        icon = QIcon()
        if base64_icon:
            try:
                pixmap = QPixmap()
                loaded = pixmap.loadFromData(base64.b64decode(base64_icon))
                if loaded and not pixmap.isNull():
                    icon = QIcon(pixmap)
                else:
                    print(f"Warning: Failed to load pixmap from base64 for language '{lang_code}' in SettingsDialog.")
            except Exception as e:
                print(f"Error creating flag icon for language '{lang_code}' in SettingsDialog: {e}")
        else:
             print(f"Warning: No base64 icon data provided for language '{lang_code}' in SettingsDialog.")
        radio_button.setIcon(icon)
        radio_button.setIconSize(QSize(24, 16))
        radio_button.setStyleSheet("""
            QRadioButton {
                spacing: 5px; /* Space between indicator (hidden) and icon */
                border: 1px solid transparent; /* No border by default */
                padding: 2px; /* Some inner padding */
                background-color: transparent;
                border-radius: 3px; /* Slightly rounded corners */
            }
            QRadioButton::indicator {
                width: 0px; /* Hide the actual radio button circle */
                height: 0px;
            }
            QRadioButton:checked {
                 border: 1px solid palette(highlight); /* Add border when selected */
                 /* background-color: palette(highlight); /* Optional: background highlight */
            }
             QRadioButton:hover {
                 background-color: palette(alternate-base); /* Subtle background on hover */
            }
        """)
        lang_name = 'English' if lang_code == 'en' else 'Русский' if lang_code == 'ru' else '中文' if lang_code == 'zh' else lang_code
        tooltip_key = f"Switch language to {lang_name}"
        radio_button.setToolTip(self.tr(tooltip_key, self.current_language))
        radio_button.setMinimumSize(QSize(30, 22))
        radio_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def get_settings(self):
        """
        Retrieves the selected settings from the dialog controls.
        Returns:
            tuple: A tuple containing:
                - selected_language (str): The language code of the selected radio button.
                - max_length (int): The value from the maximum length spinbox.
        """
        selected_language = 'en'
        if self.radio_en.isChecked():
            selected_language = 'en'
        elif self.radio_ru.isChecked():
            selected_language = 'ru'
        elif self.radio_zh.isChecked():
            selected_language = 'zh'
        max_length = self.spin_max_length.value()
        return selected_language, max_length
