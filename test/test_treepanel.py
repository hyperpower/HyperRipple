import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# ...existing code...delegate.delegate import TaskDelegate
# from view.view import View

from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel 
from model.matplot_model import MatplotModel
from model.list_model import ListModel

class TreePropertyWindow(QMainWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Property Panel")
        self.resize(400, 300)

        central_widget = QWidget(self)
        self.layout = QVBoxLayout(central_widget)

        self.tree_panel = TreePanel(model)
        self.property_panel = PropertyPanel(ListModel())
        self.layout.addWidget(self.tree_panel)
        self.layout.addWidget(self.property_panel)

        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")

    window = TreePropertyWindow(MatplotModel())
    window.show()
    sys.exit(app.exec())