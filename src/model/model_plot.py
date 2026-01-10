import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex
from PySide6.QtGui import QIcon, QColor, QBrush, QFont

class TreeNodeBase:
    def __init__(self, name="", status="Pending", parent=None):
        self.name = name
        self.status = status
        self.type   = None
        self.parent = parent
        self.children = []

        if parent is not None:
            parent.children.append(self)

    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)
        return 0

class TreeNodeFigure(TreeNodeBase):
    def __init__(self, name="", status="Pending", parent=None):
        super().__init__(name, status, parent)
        self.type = "Figure"


class TreeNodePlot(TreeNodeBase):
    def __init__(self, name="", status="Pending", parent=None):
        super().__init__(name, status, parent)
        self.type = "Plot"

    def insertFigure(self, name = "", status = "Pending"):
        figure = TreeNodeFigure(name, status, self)
        self.children.append(figure)
        return figure
