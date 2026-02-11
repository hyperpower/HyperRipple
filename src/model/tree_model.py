from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex
from .tree_node import *


class TreeModel(QAbstractItemModel):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.root = TreeNodeBase("Root")
        self.root.addChild(node)


    def rowCount(self, parent=QModelIndex()):
        node = self.getItem(parent)
        return len([child for child in node.children if not child.is_leaf()])

    def columnCount(self, parent=QModelIndex()):
        return 1  # 只显示名字

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        node = self.getItem(index)
        if node.is_leaf():
            return None # leaf node is not displayed
        if role == Qt.DisplayRole:
            return f"{node.name}"
        return None

    def index(self, row, column, parent=QModelIndex()):
        parentNode = self.getItem(parent)
        non_leaf_children = [child for child in parentNode.children if not child.is_leaf()]
        if 0 <= row < len(non_leaf_children):
            childNode = non_leaf_children[row]
            return self.createIndex(row, column, childNode)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = self.getItem(index)
        if node.parent == self.root or node.parent is None:
            return QModelIndex()
        return self.createIndex(node.parent.row(), 0, node.parent)

    def getItem(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.root

    def index_from_node(self, obj_node, parent_index=QModelIndex()):
        """
        递归查找给定节点对应的 QModelIndex。
        """
        node = self.getItem(parent_index)
        if node == obj_node:
            return parent_index
        else:
            non_leaf_children = [child for child in node.children if not child.is_leaf()]
            for row, child in enumerate(non_leaf_children):
                child_index = self.index(row, 0, parent_index)
                result = self.index_from_node(obj_node, child_index)
                if result.isValid():
                    return result
        return QModelIndex()
    
    # def print_all_rows(self, parent_index=QModelIndex(), level=0):
    #     node = self.getItem(parent_index)
    #     non_leaf_children = [child for child in node.children if not child.is_leaf()]
    #     print("  " * level + f"Node: {node.name}, rows: {len(non_leaf_children)}")
    #     for row, child in enumerate(non_leaf_children):
    #         child_index = self.index(row, 0, parent_index)
    #         self.print_all_rows(child_index, level + 1)
