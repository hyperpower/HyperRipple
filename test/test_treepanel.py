import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from model.model import TaskModel

# ...existing code...delegate.delegate import TaskDelegate
# from view.view import View

from view.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())