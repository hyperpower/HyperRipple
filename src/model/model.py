import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QAbstractItemModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption

class Task:
    def __init__(self, title: str, progress: int = 0, done: bool = False):
        self.title = title
        self.progress = progress      # 0~100
        self.done = done

class TreeItem:
    def __init__(self, name, item_type="Folder", parent=None):
        self.name = name
        self.value = None
        self.type = item_type  # 可以是 "Folder"、"File" 等

        self.parent = parent
        self.children = []

    def child(self, row):
        return self.children[row] if 0 <= row < len(self.children) else None

    def childCount(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def addChild(self, item):
        item.parent = self
        self.children.append(item)

    def removeChild(self, row):
        if 0 <= row < len(self.children):
            self.children.pop(row)

class FolderModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootItem = TreeItem("Root")

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

    # 增加 item
    def addItem(self, name, item_type="Folder", parent_index=QModelIndex()):
        parentItem = self.getItem(parent_index)
        self.beginInsertRows(parent_index, parentItem.childCount(), parentItem.childCount())
        newItem = TreeItem(name, item_type, parentItem)
        parentItem.addChild(newItem)
        self.endInsertRows()

    # 删除 item
    def removeItem(self, index):
        if not index.isValid():
            return
        item = self.getItem(index)
        parentItem = item.parent
        row = item.row()
        parent_index = self.createIndex(parentItem.row(), 0, parentItem) if parentItem != self.rootItem else QModelIndex()
        self.beginRemoveRows(parent_index, row, row)
        parentItem.removeChild(row)
        self.endRemoveRows()

    # 在某个 item 下增加子 item
    def addChildItem(self, parent_index, name, item_type="File"):
        self.addItem(name, item_type, parent_index)



if __name__ == "__main__":
    model = FolderModel()
    model.addItem("Documents", "Folder")
    model.addItem("Music", "Folder")
    item = model.getItem(model.index(0, 0, QModelIndex()))  # Music
    print(item.name)  # Photo.jpg
    # print(item.type)  # Photo.jpg
    folder_index = model.index(0, 0, QModelIndex())  # Documents
    model.addChildItem(folder_index, "Resume.docx", "File")