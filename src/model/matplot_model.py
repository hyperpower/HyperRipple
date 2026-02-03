import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QAbstractItemModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption

from matplot_node import *


class MatplotModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = MatplotNode()

    def rowCount(self, parent=QModelIndex()):
        item = self.getItem(parent)
        return item.childCount()

    def columnCount(self, parent=QModelIndex()):
        return 1  # 只显示名字

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self.getItem(index)
        if role == Qt.DisplayRole:
            return f"{item.name} ({item.type})"
        return None

    def index(self, row, column, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = self.getItem(index)
        if item.parent == self.rootItem or item.parent is None:
            return QModelIndex()
        return self.createIndex(item.parent.row(), 0, item.parent)

    def getItem(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.rootItem
    