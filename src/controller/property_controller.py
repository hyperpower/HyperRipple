import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal, QObject
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption


class PropertyController(QObject):
    def __init__(self, tree_panel, property_panel):
        super().__init__()
        # self.tree_panel = tree_panel
        # self.property_panel = property_panel

        # 连接视图的信号到控制器的槽
        tree_panel.nodeSelected.connect(property_panel.setNode)
        # 连接模型的信号到控制器的槽
        # self.model.dataChanged.connect(self.on_data_changed)

    