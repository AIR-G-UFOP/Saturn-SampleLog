import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from ..ui.generated.workspacewindow import Ui_WorkspaceWindow
from ..modules.ui_functions import UIFunctions
from ..config.ui_settings import (WORKSPACE_TOOLBAR_SELECTED, WORKSPACE_TOOLBAR_NOT_SELECTED)


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # Enables per-screen DPI awareness
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # Auto-adjust based on system settings
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class WorkspaceWindow(QtWidgets.QMainWindow):

    def __init__(self, user_service, sample_service, analysis_service, reduction_service):
        super(WorkspaceWindow, self).__init__()

        self.ui = Ui_WorkspaceWindow()
        self.ui.setupUi(self)
        UIFunctions.uiDefinitions(self)
        self.setWindowTitle("Workspace Window")

        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.resetStyle(self, "btn_workspace")
        self.ui.btn_labNotebook.setStyleSheet(UIFunctions.selectMenu(self.ui.btn_labNotebook.styleSheet()))
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageNotebook)

        self.ui.labNotebookEditor.setAcceptRichText(True)
        self.ui.labNotebookEditor.setUndoRedoEnabled(True)

        self.userService = user_service
        self.sampleService = sample_service
        self.analysisService = analysis_service
        self.reductionService = reduction_service

        self.editor = self.ui.labNotebookEditor
        self.search_results = []
        self.current_result = -1
        self.default_font_family = "Arial"
        self.default_font_size = 12

        self.ui.btn_labNotebook.clicked.connect(self.handle_book_change)
        self.ui.btn_labLog.clicked.connect(self.handle_book_change)
        self.ui.btn_bold.clicked.connect(self.set_bold)
        self.ui.btn_italic.clicked.connect(self.set_italic)
        self.ui.btn_underline.clicked.connect(self.set_underline)
        self.ui.btn_strikethrough.clicked.connect(self.set_strikethrough)
        self.ui.fontComboBox.currentFontChanged.connect(self.set_font)
        self.ui.spinBox_fontSize.textChanged.connect(self.set_font_size)
        self.ui.btn_textColour.clicked.connect(self.set_text_color)
        self.ui.btn_highlight.clicked.connect(self.set_background_color)
        self.ui.btn_alignLeft.clicked.connect(self.set_alignment)
        self.ui.btn_alignRight.clicked.connect(self.set_alignment)
        self.ui.btn_alignCentre.clicked.connect(self.set_alignment)
        self.ui.btn_alignJustify.clicked.connect(self.set_alignment)
        self.ui.btn_identPositive.clicked.connect(self.set_ident)
        self.ui.btn_identNegative.clicked.connect(self.set_ident)
        self.ui.btn_numberList.clicked.connect(self.numbered_list)
        self.ui.btn_bulletList.clicked.connect(self.bullet_list)
        self.ui.btn_undo.clicked.connect(self.undo)
        self.ui.btn_redo.clicked.connect(self.redo)
        self.ui.btn_undo.setShortcut(QtGui.QKeySequence.Undo)
        self.ui.btn_redo.setShortcut(QtGui.QKeySequence.Redo)
        self.ui.search.textChanged.connect(self.search_text)
        self.ui.btn_searchNext.clicked.connect(self.next_result)
        self.ui.btn_searchPrevious.clicked.connect(self.previous_result)
        self.ui.label_search.hide()

        self.ui.labNotebookEditor.textChanged.connect(self.handle_empty_document)
        self.ui.labNotebookEditor.cursorPositionChanged.connect(self.refresh_toolbar_states)
        self.ui.labNotebookEditor.selectionChanged.connect(self.refresh_toolbar_states)

        self.setup_editor_defaults()

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def handle_book_change(self):
        sender = self.sender()
        if sender.objectName() == "btn_labNotebook":
            self.set_sidebar_button_style(sender)
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageNotebook)
            self.editor = sender
        elif sender.objectName() == "btn_labLog":
            self.set_sidebar_button_style(sender)
            self.ui.stackedWidget.setCurrentWidget(self.ui.pageLog)
            self.editor = sender

        self.refresh_toolbar_states()

        if self.ui.search.text() != "":
            self.search_text()

    def handle_empty_document(self):
        if not self.editor.document().isEmpty():
            return
        self.editor.blockSignals(True)
        try:
            cursor = self.editor.textCursor()
            block_fmt = QtGui.QTextBlockFormat()
            block_fmt.setAlignment(QtCore.Qt.AlignLeft)
            char_fmt = QtGui.QTextCharFormat()
            char_fmt.setFontFamily(self.default_font_family)
            char_fmt.setFontPointSize(self.default_font_size)
            cursor.select(QtGui.QTextCursor.Document)
            cursor.mergeBlockFormat(block_fmt)
            cursor.mergeCharFormat(char_fmt)
            self.editor.setTextCursor(cursor)
            self.editor.setCurrentCharFormat(char_fmt)
        finally:
            self.editor.blockSignals(False)
        self.refresh_toolbar_states()

    def set_sidebar_button_style(self, sender):
        UIFunctions.resetStyle(self, sender.objectName())
        sender.setStyleSheet(UIFunctions.selectMenu(sender.styleSheet()))

    def setup_editor_defaults(self):
        font = QtGui.QFont(self.default_font_family, self.default_font_size)
        self.editor.setFont(font)
        self.editor.setFontPointSize(self.default_font_size)
        self.editor.setAlignment(QtCore.Qt.AlignLeft)
        fmt = QtGui.QTextCharFormat()
        fmt.setFontFamily(self.default_font_family)
        fmt.setFontPointSize(self.default_font_size)
        self.editor.setCurrentCharFormat(fmt)
        self.ui.fontComboBox.setCurrentFont(font)
        self.ui.spinBox_fontSize.setValue(self.default_font_size)
        self.refresh_toolbar_states()

    @staticmethod
    def update_toolbar_state(btn, state):
        if state:
            btn.setStyleSheet(WORKSPACE_TOOLBAR_SELECTED)
        else:
            btn.setStyleSheet(WORKSPACE_TOOLBAR_NOT_SELECTED)

    def get_selection_format_states(self, cursor):
        if not cursor.hasSelection():
            fmt = cursor.charFormat()
            return {
                "bold": fmt.fontWeight() == QtGui.QFont.Bold,
                "italic": fmt.fontItalic(),
                "underline": fmt.fontUnderline(),
                "strike": fmt.fontStrikeOut(),
                "font_family": fmt.fontFamily(),
                "font_size": fmt.fontPointSize()
            }
        doc = self.editor.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor = QtGui.QTextCursor(doc)
        cursor.setPosition(start)
        first = True
        states = {}
        while cursor.position() < end:
            cursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
            fmt = cursor.charFormat()
            current = {
                "bold":
                    fmt.fontWeight() == QtGui.QFont.Bold,
                "italic":
                    fmt.fontItalic(),
                "underline":
                    fmt.fontUnderline(),
                "strike":
                    fmt.fontStrikeOut(),
                "font_family":
                    fmt.fontFamily(),
                "font_size":
                    fmt.fontPointSize()
            }
            if first:
                states = current
                first = False
            else:
                for key in states:
                    if states[key] != current[key]:
                        states[key] = None
        return states

    def refresh_toolbar_states(self):
        cursor = self.editor.textCursor()
        self.ui.fontComboBox.blockSignals(True)
        self.ui.spinBox_fontSize.blockSignals(True)
        try:
            states = self.get_selection_format_states(cursor)
            self.update_toolbar_state(self.ui.btn_bold, states["bold"] is True)
            self.update_toolbar_state(self.ui.btn_italic, states["italic"] is True)
            self.update_toolbar_state(self.ui.btn_underline, states["underline"] is True)
            self.update_toolbar_state(self.ui.btn_strikethrough, states["strike"] is True)
            if states["font_family"] is not None:
                self.ui.fontComboBox.setCurrentFont(QtGui.QFont(states["font_family"]))
            else:
                self.ui.fontComboBox.setCurrentIndex(11)
            if states["font_size"] is not None:
                self.ui.spinBox_fontSize.setValue(int(states["font_size"]) )
            else:
                self.ui.spinBox_fontSize.clear()
            alignment = self.editor.alignment()
            self.update_toolbar_state(self.ui.btn_alignLeft, alignment == QtCore.Qt.AlignLeft)
            self.update_toolbar_state(self.ui.btn_alignCentre, alignment == QtCore.Qt.AlignCenter)
            self.update_toolbar_state(self.ui.btn_alignRight, alignment == QtCore.Qt.AlignRight)
            self.update_toolbar_state(self.ui.btn_alignJustify, alignment == QtCore.Qt.AlignJustify)
            current_list = cursor.currentList()
            is_bullet = (current_list and current_list.format().style() == QtGui.QTextListFormat.ListDisc)
            is_numbered = (current_list and current_list.format().style() == QtGui.QTextListFormat.ListDecimal)
            self.update_toolbar_state(self.ui.btn_bulletList, is_bullet)
            self.update_toolbar_state(self.ui.btn_numberList, is_numbered)
        finally:
            self.ui.fontComboBox.blockSignals(False)
            self.ui.spinBox_fontSize.blockSignals(False)

    def merge_text_format(self, fmt):
        cursor = self.editor.textCursor()
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def set_bold(self):
        new_state = self.editor.fontWeight() != QtGui.QFont.Bold
        fmt = QtGui.QTextCharFormat()
        fmt.setFontWeight(QtGui.QFont.Bold if new_state else QtGui.QFont.Normal)
        self.merge_text_format(fmt)
        self.update_toolbar_state(self.sender(), new_state)

    def set_italic(self):
        new_state = not self.editor.fontItalic()
        fmt = QtGui.QTextCharFormat()
        fmt.setFontItalic(new_state)
        self.merge_text_format(fmt)
        self.update_toolbar_state(self.sender(), new_state)

    def set_underline(self):
        new_state = not self.editor.fontUnderline()
        fmt = QtGui.QTextCharFormat()
        fmt.setFontUnderline(new_state)
        self.merge_text_format(fmt)
        self.update_toolbar_state(self.sender(), new_state)

    def set_strikethrough(self):
        current = self.editor.currentCharFormat()
        new_state = not current.fontStrikeOut()
        fmt = QtGui.QTextCharFormat()
        fmt.setFontStrikeOut(new_state)
        self.merge_text_format(fmt)
        self.update_toolbar_state(self.sender(), new_state)

    def set_font(self, font):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.merge_text_format(fmt)

    def set_font_size(self, size):
        fmt = QtGui.QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self.merge_text_format(fmt)

    @staticmethod
    def get_colour():
        return QtWidgets.QColorDialog.getColor()

    def set_text_color(self):
        colour = self.get_colour()
        if colour.isValid():
            fmt = QtGui.QTextCharFormat()
            fmt.setForeground(colour)
            self.merge_text_format(fmt)

    def set_background_color(self):
        colour = self.get_colour()
        if colour.isValid():
            fmt = QtGui.QTextCharFormat()
            fmt.setBackground(colour)
            self.merge_text_format(fmt)

    @staticmethod
    def get_alignment(btn):
        if btn.objectName() == "btn_alignLeft":
            return QtCore.Qt.AlignLeft
        elif btn.objectName() == "btn_alignCentre":
            return QtCore.Qt.AlignCenter
        elif btn.objectName() == "btn_alignRight":
            return QtCore.Qt.AlignRight
        elif btn.objectName() == "btn_alignJustify":
            return QtCore.Qt.AlignJustify
        return None

    def set_alignment(self):
        btn = self.sender()
        alignment = self.get_alignment(btn)
        cursor = self.editor.textCursor()
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(alignment)
        cursor.mergeBlockFormat(block_fmt)
        for b in (
                self.ui.btn_alignLeft,
                self.ui.btn_alignCentre,
                self.ui.btn_alignRight,
                self.ui.btn_alignJustify
        ):
            self.update_toolbar_state(b, False)
        self.update_toolbar_state(btn, True)

    def bullet_list(self):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        current_list = cursor.currentList()
        active = False
        if current_list and (current_list.format().style() == QtGui.QTextListFormat.ListDisc):
            block_fmt = cursor.blockFormat()
            block_fmt.setObjectIndex(-1)
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
        else:
            if current_list:
                list_fmt = current_list.format()
            else:
                list_fmt = QtGui.QTextListFormat()
            list_fmt.setStyle(QtGui.QTextListFormat.ListDisc)
            cursor.createList(list_fmt)
            active = True
        cursor.endEditBlock()
        self.update_toolbar_state(self.ui.btn_bulletList, active)
        self.update_toolbar_state(self.ui.btn_numberList, False)

    def numbered_list(self):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        current_list = cursor.currentList()
        active = False
        if current_list and (current_list.format().style() == QtGui.QTextListFormat.ListDecimal):
            block_fmt = cursor.blockFormat()
            block_fmt.setObjectIndex(-1)
            block_fmt.setIndent(0)
            cursor.setBlockFormat(block_fmt)
        else:
            if current_list:
                list_fmt = current_list.format()
            else:
                list_fmt = QtGui.QTextListFormat()
            list_fmt.setStyle(QtGui.QTextListFormat.ListDecimal)
            cursor.createList(list_fmt)
            active = True
        cursor.endEditBlock()
        self.update_toolbar_state(self.ui.btn_numberList, active)
        self.update_toolbar_state(self.ui.btn_bulletList, False)

    @staticmethod
    def get_ident(btn):
        if btn.objectName() == "btn_identPositive":
            return +20
        else:
            return -20

    def set_ident(self):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        block = cursor.document().findBlock(cursor.selectionStart())
        end = cursor.selectionEnd()
        while block.isValid() and block.position() <= end:
            cursor.setPosition(block.position())
            fmt = block.blockFormat()
            fmt.setLeftMargin(fmt.leftMargin() + self.get_ident(self.sender()))
            cursor.setBlockFormat(fmt)
            block = block.next()
        cursor.endEditBlock()

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def search_text(self):
        text = self.ui.search.text()
        self.search_results = []
        self.current_result = -1
        extra_selections = []
        if not text:
            self.editor.setExtraSelections([])
            self.ui.label_search.setText("0/0")
            self.ui.label_search.hide()
            return
        flags = QtGui.QTextDocument.FindFlags()
        cursor = self.editor.document().find(text, 0, flags)
        while not cursor.isNull():
            self.search_results.append((cursor.selectionStart(), cursor.selectionEnd()))
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(QtGui.QColor("#FFD54F") )
            selection.format.setForeground(QtGui.QColor("#000000"))
            extra_selections.append(selection)
            cursor = self.editor.document().find(text, cursor, flags)
        self.editor.setExtraSelections(extra_selections)
        if self.search_results:
            self.current_result = -1
            self.ui.label_search.show()
            self.ui.label_search.setText(f"0/{len(self.search_results)}")
        else:
            self.ui.label_search.setText("0/0")
            self.ui.label_search.hide()

    def goto_result(self, index):
        if not self.search_results:
            return
        start, end = self.search_results[index]
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)
        self.update_highlights(index)
        self.ui.label_search.show()
        self.ui.label_search.setText(f"{index + 1}/{len(self.search_results)}")

    def update_highlights(self, current_index):
        extra_selections = []
        for i, (start, end) in enumerate(self.search_results):
            cursor = self.editor.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.cursor = cursor
            if i == current_index:
                selection.format.setBackground(QtGui.QColor("#50FA7B"))
                selection.format.setForeground(QtGui.QColor("#000000"))
            else:
                selection.format.setBackground(QtGui.QColor("#C8F7C5"))
                selection.format.setForeground(QtGui.QColor("#000000"))
            extra_selections.append(selection)
        self.editor.setExtraSelections(extra_selections)

    def next_result(self):
        if not self.search_results:
            return
        self.current_result += 1
        if self.current_result >= len(self.search_results):
            self.current_result = 0
        self.goto_result(self.current_result)

    def previous_result(self):
        if not self.search_results:
            return
        self.current_result -= 1
        if self.current_result < 0:
            self.current_result = len(self.search_results) - 1
        self.goto_result(self.current_result)