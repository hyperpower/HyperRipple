import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
from model.matplot_model import MatplotModel
from model.model import FolderModel, TaskModel
from delegate.delegate import TaskDelegate
# from view.view import View
from controller.controller import TaskController
from view.main_window import MainWindow
from view.tree_panel import TreeWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")

    window = TreeWindow(MatplotModel())
    window.show()
    sys.exit(app.exec())