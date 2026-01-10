import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption

class Task:
    def __init__(self, title: str, progress: int = 0, done: bool = False):
        self.title = title
        self.progress = progress      # 0~100
        self.done = done


class TaskModel(QAbstractListModel):
    # 自定义角色
    ProgressRole = Qt.UserRole + 1
    DoneRole = Qt.UserRole + 2

    dataChanged = Signal(QModelIndex, QModelIndex)  # 方便外部知道变化

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: list[Task] = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._tasks) if not parent.isValid() else 0

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        task = self._tasks[index.row()]

        if role == Qt.DisplayRole:
            return task.title
        elif role == Qt.DecorationRole:
            return "✔" if task.done else "⬜"
        elif role == self.ProgressRole:
            return task.progress
        elif role == self.DoneRole:
            return task.done
        return None

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        task = self._tasks[index.row()]

        if role == self.ProgressRole:
            task.progress = max(0, min(100, int(value)))
            self.dataChanged.emit(index, index, [self.ProgressRole])
            return True
        elif role == self.DoneRole:
            task.done = bool(value)
            self.dataChanged.emit(index, index, [self.DoneRole, Qt.DecorationRole])
            return True

        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def addTask(self, title: str):
        self.beginInsertRows(QModelIndex(), len(self._tasks), len(self._tasks))
        self._tasks.append(Task(title))
        self.endInsertRows()

    def removeTask(self, row: int):
        if 0 <= row < len(self._tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._tasks.pop(row)
            self.endRemoveRows()

    def getTask(self, row: int) -> Task | None:
        if 0 <= row < len(self._tasks):
            return self._tasks[row]
        return None