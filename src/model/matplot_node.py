import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex
from PySide6.QtGui import QIcon, QColor, QBrush, QFont

from .tree_node import *

class FigureNode(TreeNodeGroup):
    def __init__(self, name="Figure"):
        super().__init__(name)

        # add default children
        self.addChild(TreeNodeString("title", "My Figure"))
        self.addChild(TreeNodeNumber("width", 800))
        self.addChild(TreeNodeNumber("height", 600))


class MatplotNode(TreeNodeGroup):
    def __init__(self, name="Matplot"):
        super().__init__(name)

        # add default children
        self.addChild(TreeNodeString("version", "3.5.1"))
        # self.addChild(TreeNodeNumber("test number", 1))



