from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex 

class TableModel(QAbstractTableModel):
    def __init__(self, node=None, parent=None):
        super().__init__(parent)
        self.node = node
        self.leaf_children = []
        if node is not None:
            self._update_leaf_children()

    def setNode(self, node):
        self.beginResetModel()
        self.node = node
        self._update_leaf_children()
        self.endResetModel()

    def _update_leaf_children(self):
        if self.node is None:
            self.leaf_children = []
        else:
            self.leaf_children = [child for child in self.node.children if child.is_leaf()]

    def rowCount(self, parent=QModelIndex()):
        return len(self.leaf_children)

    def columnCount(self, parent=QModelIndex()):
        return 2  # 名称和数值

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self.node is None:
            return None
        if index.row() >= len(self.leaf_children):
            return None
        child = self.leaf_children[index.row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return child.name
            elif index.column() == 1:
                return getattr(child, 'value', '')
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or self.node is None:
            return False
        if index.column() != 1:
            return False
        child = self.leaf_children[index.row()]
        if role == Qt.EditRole:
            child.value = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        child = self.leaf_children[index.row()] if index.isValid() and index.row() < len(self.leaf_children) else None
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 1 and child is not None and child.is_editable():
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["名称", "数值"][section]
        return None