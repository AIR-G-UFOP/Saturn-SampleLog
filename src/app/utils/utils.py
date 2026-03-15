from PyQt5 import QtWidgets

def get_maximum_height(layout):
    final_height = 50
    for i in range(layout.count()):
        panel_height = 0
        for label in layout.itemAt(i).widget().findChildren(QtWidgets.QLabel):
            panel_height += label.sizeHint().height() + 6
        if panel_height > final_height:
            final_height = panel_height
    return final_height + 36
