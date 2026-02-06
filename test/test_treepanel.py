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

from controller.property_controller import PropertyController
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel 
from model.matplot_model import MatplotModel
from model.table_model import TableModel
from view.main_window import MainWindow

class TreePropertyWindow(QMainWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Property Panel")
        self.resize(400, 300)

        central_widget = QWidget(self)
        self.layout = QVBoxLayout(central_widget)

        self.tree_panel = TreePanel(model)
        node = model.getItem(QModelIndex())
        self.property_panel = PropertyPanel(TableModel(node))
        self.layout.addWidget(self.tree_panel)
        self.layout.addWidget(self.property_panel)

        self.setCentralWidget(central_widget)

        self.controller = PropertyController(self.tree_panel, self.property_panel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")

    window = TreePropertyWindow(MatplotModel())
    # window = MainWindow(MatplotModel())
    window.show()
    sys.exit(app.exec())