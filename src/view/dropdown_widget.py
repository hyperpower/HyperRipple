from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolButton, QSizePolicy
from PySide6.QtCore import QSize, Qt

from view.view_helper import createThemedIcon


class DropDownWidget(QWidget):
    """可折叠的下拉式Widget，提供toggle button和折叠/展开功能"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._title = title
        self._content_builder = None
        # self._collapsed = False 
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        layout = QVBoxLayout(self)
        
        # 创建toggle按钮
        self._toggle_btn = QToolButton(self)
        self._toggle_btn.setText(title)
        self._toggle_btn.setArrowType(Qt.NoArrow)
        _icon = createThemedIcon("asset/icons/right_circle.svg")
        self._toggle_btn.setIcon(_icon)
        self._toggle_btn.setIconSize(QSize(18, 18))
        self._toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._toggle_btn.setAutoRaise(True)
        self._toggle_btn.setFixedHeight(24)
        self._toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._toggle_btn.clicked.connect(self._toggle_dropdown)
        layout.addWidget(self._toggle_btn)
        
        # 创建内容容器
        self._content = QWidget(self)
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self._content.setVisible(False)
        
        layout.addWidget(self._content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        # self.setCollapsed(True)
        # self._toggle_dropdown()


    def _clear_content(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            child_widget = item.widget()
            child_layout = item.layout()
            if child_widget is not None:
                child_widget.setParent(None)
                child_widget.deleteLater()
            if child_layout is not None:
                while child_layout.count():
                    sub_item = child_layout.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget is not None:
                        sub_widget.setParent(None)
                        sub_widget.deleteLater()

    def _rebuild_content(self):
        if self._content_builder is None:
            return
        self._clear_content()
        widget = self._content_builder()
        if widget is not None:
            self._content_layout.addWidget(widget)

    def _update_layout_state(self):
        print("Updating layout state, collapsed:", self.isCollapsed())
        collapsed = self.isCollapsed()
        header_h = self._toggle_btn.sizeHint().height()
        if not collapsed:
            self.setMaximumHeight(header_h)
        else:
            self.setMaximumHeight(16777215)
        self.updateGeometry()
        parent = self.parentWidget()
        if parent is not None and parent.layout() is not None:
            parent.layout().activate()
    
    def _toggle_dropdown(self):
        """处理折叠/展开"""
        print("Toggling dropdown, collapsed:", self.isCollapsed())
        collapsed = self.isCollapsed()
        if collapsed:
            self._rebuild_content()
            self._update_layout_state()
            self._content.setVisible(True)
        else:
            self._clear_content()
            self._update_layout_state()
            self._content.setVisible(False)
        if collapsed:
            _icon = createThemedIcon("asset/icons/down_circle.svg")
        else:
            _icon = createThemedIcon("asset/icons/right_circle.svg")
        self._toggle_btn.setIcon(_icon)
        # self._update_layout_state()

    def setContentBuilder(self, builder):
        self._content_builder = builder
        if not self.isCollapsed():
            self._rebuild_content()
    
    def setContent(self, widget):
        """设置内容widget"""
        self._content_builder = None
        self._clear_content()
        self._content_layout.addWidget(widget)
    
    def getContent(self):
        """获取内容容器"""
        return self._content
    
    def setCollapsed(self, collapsed):
        """设置折叠状态"""
        if collapsed:
            self._content.setVisible(False)
            self._clear_content()
        else:
            self._rebuild_content()
            self._content.setVisible(True)
        if collapsed:
            _icon = createThemedIcon("asset/icons/right_circle.svg")
        else:
            _icon = createThemedIcon("asset/icons/down_circle.svg")
        self._toggle_btn.setIcon(_icon)
        self._update_layout_state()
    
    def isCollapsed(self):
        return not self._content.isVisible()
