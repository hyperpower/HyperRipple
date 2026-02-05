from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex
from .tree_node import *


class TreeModel(QAbstractItemModel):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.root = node

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
            return f"{item.name}"
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
        if item.parent == self.root or item.parent is None:
            return QModelIndex()
        return self.createIndex(item.parent.row(), 0, item.parent)

    def getItem(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.root
    