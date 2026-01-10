import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption


from model.model import TaskModel

class TaskDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 60) 

    def paint(self, painter: QPainter, option, index: QModelIndex):
        painter.save()

        task_title = index.data(Qt.DisplayRole)
        progress = index.data(TaskModel.ProgressRole)
        is_done = index.data(TaskModel.DoneRole)

        rect = option.rect

        # 背景
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, QColor(80, 120, 200, 180))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(rect, QColor(240, 240, 255))
        else:
            painter.fillRect(rect, QColor(245, 245, 250))

        # 复选框区域
        check_rect = rect.adjusted(8, 8, -8, -8)
        check_rect.setWidth(40)

        # 绘制完成状态
        check_color = QColor("#4CAF50") if is_done else QColor("#9E9E9E")
        painter.setPen(check_color)
        painter.setBrush(check_color)
        painter.drawRoundedRect(check_rect.adjusted(4,4,-4,-4), 6, 6)

        if is_done:
            painter.setPen(Qt.white)
            painter.drawText(check_rect, Qt.AlignCenter, "✓")

        # 文字区域
        text_rect = rect.adjusted(60, 10, -70, -25)
        font = QFont("Microsoft YaHei", 11)
        if is_done:
            font.setStrikeOut(True)
        painter.setFont(font)
        painter.setPen(QColor("#333") if not is_done else QColor("#888"))
        option = QTextOption()
        option.setWrapMode(QTextOption.NoWrap)
        painter.drawText(text_rect, task_title, option)

        # 进度条
        progress_rect = rect.adjusted(60, 35, -70, -8)
        painter.setPen(Qt.NoPen)
        # 背景灰条
        painter.setBrush(QBrush(QColor(220, 220, 220)))
        painter.drawRoundedRect(progress_rect, 4, 4)

        # 前景进度
        if progress > 0:
            fill_rect = progress_rect.adjusted(0,0,0,0)
            fill_rect.setWidth(int(progress_rect.width() * (progress / 100)))
            painter.setBrush(QBrush(QColor("#4CAF50")))
            painter.drawRoundedRect(fill_rect, 4, 4)

        # 进度文字
        prog_text = f"{progress}%"
        painter.setPen(QColor("#555"))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(progress_rect, Qt.AlignRight | Qt.AlignVCenter, prog_text)

        painter.restore()

    def editorEvent(self, event, model, option, index):
        # 点击复选框区域切换完成状态
        if event.type() == event.MouseButtonRelease:
            check_rect = option.rect.adjusted(8, 8, -8, -8)
            check_rect.setWidth(40)

            if check_rect.contains(event.pos()):
                current_done = model.data(index, TaskModel.DoneRole)
                model.setData(index, not current_done, TaskModel.DoneRole)
                return True

        return super().editorEvent(event, model, option, index)