import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption


from model.model import TaskModel

class TaskController:
    def __init__(self, model: TaskModel, view: QListView):
        self.model = model
        self.view = view

        # 连接信号（如果有的话）
        self.model.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self, topLeft, bottomRight, roles):
        """可以在这里做一些额外的业务逻辑"""
        pass

    def add_new_task(self, title: str):
        if not title.strip():
            return
        self.model.addTask(title.strip())

    def delete_selected_task(self):
        indexes = self.view.selectedIndexes()
        if not indexes:
            return

        # 因为删除会改变索引，所以要从后往前删
        rows = sorted([i.row() for i in indexes], reverse=True)
        for row in rows:
            self.model.removeTask(row)