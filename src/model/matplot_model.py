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
    # Explicitly expose a dataChanged signal with the same signature as QAbstractItemModel.
    dataChanged = Signal(QModelIndex, QModelIndex, list)
    def __init__(self, parent=None):
        super().__init__(MatplotRootNode(), parent)
        root_index = self.index(0,0)
        self.addFigureNode(root_index, "Figure 1", "Figure")

    def addFigureNode(self, parent_index: QModelIndex, name: str, item_type: str):
        parent_item = self.getItem(parent_index)
        non_leaf_children = [child for child in parent_item.children if not child.is_leaf()]
        row = len(non_leaf_children)

        self.beginInsertRows(parent_index, row, row)
        new_item = FigureNode(name)
        parent_item.addChild(new_item)
        self.endInsertRows()

        new_index = self.index(row, 0, parent_index)
        self.dataChanged.emit(new_index, new_index, [Qt.DisplayRole])