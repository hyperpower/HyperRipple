from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar, QApplication
)
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QAction, QIcon, QPalette, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

from view.view_helper import *


class FigPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.current_mode = None
        
        # 创建自定义工具栏
        self.toolbar = QToolBar("工具栏", self)
        self.toolbar.setMovable(False)
        
        # 放大按钮
        icon_zoom = QIcon()
        icon_zoom.addPixmap(createThemedPixmap("asset/icons/zoom.svg"), QIcon.Normal, QIcon.Off)
        icon_zoom.addPixmap(createThemedPixmap("asset/icons/zoom.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        self.zoom_action = QAction(icon_zoom, "Zoom", self)
        self.zoom_action.setCheckable(True)
        self.zoom_action.triggered.connect(self._on_zoom_clicked)
        self.toolbar.addAction(self.zoom_action)
        
        # 移动按钮
        icon_pan = QIcon()
        icon_pan.addPixmap(createThemedPixmap("asset/icons/hand.svg"), QIcon.Normal, QIcon.Off)
        icon_pan.addPixmap(createThemedPixmap("asset/icons/hand.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        self.pan_action = QAction(icon_pan, "Pan", self)
        self.pan_action.setCheckable(True)
        self.pan_action.triggered.connect(self._on_pan_clicked)
        self.toolbar.addAction(self.pan_action)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    
    def _on_zoom_clicked(self):
        if self.zoom_action.isChecked():
            self.pan_action.setChecked(False)
            self.current_mode = 'zoom'
            self.canvas.set_mode('zoom')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_pan_clicked(self):
        if self.pan_action.isChecked():
            self.zoom_action.setChecked(False)
            self.current_mode = 'pan'
            self.canvas.set_mode('pan')
            self.canvas.setCursor(Qt.OpenHandCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()