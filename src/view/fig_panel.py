from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from view.fig_panel_toolbar import FigPanelToolbar


class FigPanel(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self._canvas = canvas
        self._current_mode = None
        
        # 创建自定义工具栏
        self.toolbar = FigPanelToolbar(self._canvas, self)
        
        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self._canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
    
    @property
    def canvas(self):
        """获取 canvas 对象。"""
        return self._canvas
    
    @property
    def current_mode(self) -> str | None:
        """获取当前模式。"""
        return self._current_mode
    
    def set_mode(self, mode: str | None):
        """设置当前模式。"""
        self._current_mode = mode
