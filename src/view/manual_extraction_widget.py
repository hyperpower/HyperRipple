from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import QSize

from view.dropdown_widget import DropDownWidget


class ManualExtractionWidget(DropDownWidget):
    """手动提取widget，包含增加、调整、删除按钮"""
    
    def __init__(self, parent=None):
        super().__init__("手动提取", parent)
        self.add_btn = None
        self.adjust_btn = None
        self.delete_btn = None
        self.setContentBuilder(self._build_content_widget)
        self.setMinimumWidth(220)
        self.setCollapsed(False)

    def _build_content_widget(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 创建按钮布局
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("增加", self)
        adjust_btn = QPushButton("调整", self)
        delete_btn = QPushButton("删除", self)
        
        # 连接信号（暂时为空，由外部设置）
        self.add_btn = add_btn
        self.adjust_btn = adjust_btn
        self.delete_btn = delete_btn
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(adjust_btn)
        buttons_layout.addWidget(delete_btn)
        
        content_layout.addLayout(buttons_layout)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        return content_widget
