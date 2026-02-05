import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QAbstractItemModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption

from .matplot_node import *
from .tree_model import *


class MatplotModel(TreeModel):
    def __init__(self, parent=None):
        super().__init__(MatplotNode(), parent)
        self.addFigureItem(self.index(0, 0), "Figure 1", "Figure")

    def addFigureItem(self, parent_index: QModelIndex, name: str, item_type: str):
        parent_item = self.getItem(parent_index)
        new_item = FigureNode(name)
        parent_item.addChild(new_item)