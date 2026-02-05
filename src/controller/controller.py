import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal, QObject
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption


from model.model import TaskModel

class TaskController(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

        # 连接视图的信号到控制器的槽
        self.view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        # 连接模型的信号到控制器的槽
        self.model.dataChanged.connect(self.on_data_changed)

    def on_selection_changed(self, selected, deselected):
        # 处理选中变化（如启用/禁用按钮等）
        pass

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