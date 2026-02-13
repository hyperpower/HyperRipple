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
        self.actions = {}
        
        # 创建自定义工具栏
        self.toolbar = QToolBar("工具栏", self)
        self.toolbar.setMovable(False)
        self._init_actions()
        
        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def _init_actions(self):
        # 放大按钮
        icon_zoom = QIcon()
        icon_zoom.addPixmap(createThemedPixmap("asset/icons/zoom.svg"), QIcon.Normal, QIcon.Off)
        icon_zoom.addPixmap(createThemedPixmap("asset/icons/zoom.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        zoom_action = QAction(icon_zoom, "Zoom", self)
        zoom_action.setCheckable(True)
        zoom_action.triggered.connect(self._on_zoom_clicked)
        self.toolbar.addAction(zoom_action)
        self.actions['zoom'] = zoom_action

        # 移动按钮
        icon_pan = QIcon()
        icon_pan.addPixmap(createThemedPixmap("asset/icons/hand.svg"), QIcon.Normal, QIcon.Off)
        icon_pan.addPixmap(createThemedPixmap("asset/icons/hand.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        pan_action = QAction(icon_pan, "Pan", self)
        pan_action.setCheckable(True)
        pan_action.triggered.connect(self._on_pan_clicked)
        self.toolbar.addAction(pan_action)
        self.actions['pan'] = pan_action

        # 添加点按钮
        icon_add_point = QIcon()
        icon_add_point.addPixmap(createThemedPixmap("asset/icons/add_point.svg"), QIcon.Normal, QIcon.Off)
        icon_add_point.addPixmap(createThemedPixmap("asset/icons/add_point.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        add_point_action = QAction(icon_add_point, "Add Point", self)
        add_point_action.setCheckable(True)
        add_point_action.triggered.connect(self._on_add_point_clicked)
        self.toolbar.addAction(add_point_action)
        self.actions['add_point'] = add_point_action

        # 笔刷按钮
        icon_brush = QIcon()
        icon_brush.addPixmap(createThemedPixmap("asset/icons/brush.svg"), QIcon.Normal, QIcon.Off)
        icon_brush.addPixmap(createThemedPixmap("asset/icons/brush.svg", color='#007AFF'), QIcon.Normal, QIcon.On)
        brush_action = QAction(icon_brush, "Brush", self)
        brush_action.setCheckable(True)
        brush_action.triggered.connect(self._on_brush_clicked)
        self.toolbar.addAction(brush_action)
        self.actions['brush'] = brush_action

    def reset_other_actions(self, key):
        for k, action in self.actions.items():
            if k != key:
                action.setChecked(False)
    
    def _on_zoom_clicked(self):
        if self.actions['zoom'].isChecked():
            self.reset_other_actions('zoom')
            self.current_mode = 'zoom'
            self.canvas.set_mode('zoom')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_pan_clicked(self):
        if self.actions['pan'].isChecked():
            self.reset_other_actions('pan')
            self.current_mode = 'pan'
            self.canvas.set_mode('pan')
            self.canvas.setCursor(Qt.OpenHandCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()

    def _on_add_point_clicked(self):
        if self.actions['add_point'].isChecked():
            self.reset_other_actions('add_point')
            self.current_mode = 'add_point'
            self.canvas.set_mode('add_point')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()

    def _on_brush_clicked(self):
        if self.actions['brush'].isChecked():
            self.reset_other_actions('brush')
            self.current_mode = 'brush'
            self.canvas.set_mode('brush')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.current_mode = None
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()