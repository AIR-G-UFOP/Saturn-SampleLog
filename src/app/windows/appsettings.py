import re
from PyQt5 import QtWidgets, QtCore
from ..utils.utils import (highlight_invalid_field, clear_highlight_field)

class Settings:
    def __init__(self, ui, settings_service):
        self.ui = ui
        self.settings_service = settings_service
        # self.settings_service.initSettings()
        self.frags = self.settings_service.DEFAULT_FILE_NAME_SETTINGS["template"]
        self.sep = self.settings_service.DEFAULT_FILE_NAME_SETTINGS["separator"]

        self.load_file_name_settings()

        self.ui.listFrag.model().rowsMoved.connect(self.update_file_name_preview)
        self.ui.separator.textChanged.connect(self.update_file_name_preview)
        self.ui.btn_addFrag.clicked.connect(self.add_fragment)
        self.ui.btn_removeFrag.clicked.connect(self.remove_fragment)
        self.ui.btn_saveFileGen.clicked.connect(self.save_file_name_settings)

    def load_file_name_settings(self):
        try:
            config = self.settings_service.getFileNameSettings()
            self.frags = config.get("template")
            self.sep = config.get("separator")

        except Exception as e:
            self.frags = self.settings_service.DEFAULT_FILE_NAME_SETTINGS["template"]
            self.sep = self.settings_service.DEFAULT_FILE_NAME_SETTINGS["separator"]
            print(e)

        self.ui.separator.blockSignals(True)
        self.ui.separator.clear()
        self.ui.separator.setText(self.sep)
        self.ui.separator.blockSignals(False)
        self.ui.listFrag.clear()
        default_frags = ["Current date", "Status date", "Analysis/Reduction name", "Operator/Handler name",
                         "Equipment"]
        for frag in self.frags:
            if frag not in default_frags:
                self.add_custom_fragment(frag)
            else:
                self.ui.listFrag.addItem(frag)
        self.update_file_name_preview()

    def update_file_name_preview(self):
        fragments = self.get_fragments()
        separator = self.ui.separator.text()
        if self.validate_separator(separator):
            clear_highlight_field(self.ui.separator)
            name = separator.join(fragments)
            self.ui.preview.setText(name)
            self.frags = fragments
            self.sep = separator
        else:
            highlight_invalid_field(self.ui.separator)
            self.status_message(f'Invalid separator. Avoid characters: {r'[]<>:\"/\\|?*,.'}')

    def add_fragment(self):
        text = self.ui.fragment.currentText()
        if text == "Custom text":
            self.add_custom_fragment("Add custom text here")
        else:
            item = QtWidgets.QListWidgetItem(text)
            self.ui.listFrag.addItem(item)
        self.update_file_name_preview()

    def add_custom_fragment(self, text):
        item = QtWidgets.QLineEdit(text)
        item.textChanged.connect(self.update_file_name_preview)
        self.ui.listFrag.addItem(text)
        self.ui.listFrag.setItemWidget(self.ui.listFrag.item(self.ui.listFrag.count() - 1), item)

    def remove_fragment(self):
        row = self.ui.listFrag.currentRow()
        if row >= 0:
            self.ui.listFrag.takeItem(row)
        self.update_file_name_preview()

    def get_fragments(self):
        fragments = []
        for i in range(self.ui.listFrag.count()):
            item = self.ui.listFrag.item(i)
            widget = self.ui.listFrag.itemWidget(item)
            if isinstance(widget, QtWidgets.QLineEdit):
                fragments.append(self.validate_custom_text(widget.text()))
            else:
                fragments.append(item.text())
        return fragments

    @staticmethod
    def validate_separator(sep):
        return sep not in r'[]<>:"/\|?*,.'

    @staticmethod
    def validate_custom_text(text):
        invalid = r'[<>:"/\\|?*\x00-\x1F]'
        return re.sub(invalid, "", text)

    def save_file_name_settings(self):
        if self.frags:
            config = {
                "template": self.frags,
                "separator": self.sep
            }
            clear_highlight_field(self.ui.listFrag)
            try:
                result = self.settings_service.saveFileNameSettings(config)
                self.status_message(result)
            except Exception as e:
                print(e)
        else:
            highlight_invalid_field(self.ui.listFrag)
            self.status_message("No fragments selected")

    def status_message(self, message):
        QtCore.QTimer.singleShot(0, lambda: self.ui.label_status.setText(message))
        QtCore.QTimer.singleShot(5000, lambda: self.ui.label_status.setText(""))

