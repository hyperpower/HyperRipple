from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

class ListModel(QAbstractListModel):
    def __init__(self, node=None, parent=None):
        super().__init__(parent)
        self.node = node  # 当前选中的树节点

    def setNode(self, node):
        self.beginResetModel()
        self.node = node
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if self.node is None:
            return 0
        return len(self.node.children)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self.node is None:
            return None
        child = self.node.children[index.row()]
        if role == Qt.DisplayRole:
            return f"{child.name}: {getattr(child, 'value', '')}"
        return None