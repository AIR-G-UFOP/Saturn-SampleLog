import os
import sys
import re
from PyQt5 import QtWidgets, QtCore
from ..utils.utils import (highlight_invalid_field, clear_highlight_field)

class Settings:
    def __init__(self, ui):
        self.ui = ui

        self.ui.listFrag.model().rowsMoved.connect(self.update_file_name_preview)
        self.ui.separator.textChanged.connect(self.update_file_name_preview)
        self.ui.btn_addFrag.clicked.connect(self.add_fragment)
        self.ui.btn_removeFrag.clicked.connect(self.remove_fragment)

    def update_file_name_preview(self):
        fragments = self.get_fragments()
        separator = self.ui.separator.text()
        if self.validate_separator(separator):
            clear_highlight_field(self.ui.separator)
            name = separator.join(fragments)
            self.ui.preview.setText(name)
        else:
            highlight_invalid_field(self.ui.separator)

    def add_fragment(self):
        text = self.ui.fragment.currentText()
        if text == "Custom text":
            item = QtWidgets.QLineEdit("Add custom text here")
            item.textChanged.connect(self.update_file_name_preview)
            self.ui.listFrag.addItem("")
            self.ui.listFrag.setItemWidget(self.ui.listFrag.item(self.ui.listFrag.count() - 1), item)
        else:
            item = QtWidgets.QListWidgetItem(text)
            self.ui.listFrag.addItem(item)
        self.update_file_name_preview()

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

