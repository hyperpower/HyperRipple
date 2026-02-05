import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QTreeView,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
from model.model import TaskModel
from delegate.delegate import TaskDelegate
# from view.view import View
from controller.controller import TaskController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("任务管理器 - MVC风格")
        self.resize(680, 520)

        # Model
        self.model = TaskModel()

        # View - QListView
        self.task_list = QTreeView()
        self.task_list.setModel(self.model)
        self.task_list.setItemDelegate(TaskDelegate())
        # self.task_list.setSpacing(4)
        # self.task_list.setUniformItemSizes(False)

        # Controller
        self.controller = TaskController(self.model, self.task_list)

        # UI 布局
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        layout.addWidget(self.task_list)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_add = QPushButton("＋ 新任务")
        self.btn_add.clicked.connect(self.on_add_clicked)
        btn_layout.addWidget(self.btn_add)

        self.btn_del = QPushButton("删除选中")
        self.btn_del.clicked.connect(self.controller.delete_selected_task)
        btn_layout.addWidget(self.btn_del)

        layout.addLayout(btn_layout)

        self.setCentralWidget(central)

        # 初始化一些测试数据
        for title in [
            "写周报", "买猫粮", "健身房 1小时", "复习 PySide6 委托绘制",
            "整理桌面", "看完《权游》前三季"
        ]:
            self.model.addTask(title)

    def on_add_clicked(self):
        # 简单演示，实际项目中可以用 QInputDialog
        from datetime import datetime
        title = f"任务 {datetime.now().strftime('%H:%M:%S')}"
        self.controller.add_new_task(title)