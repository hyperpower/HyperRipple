from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QDoubleSpinBox, QComboBox, QCheckBox,
    QPushButton, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize

from view.dropdown_widget import DropDownWidget
from view.canvas_crop_tool import CanvasCropTool


class CropToolWidget(DropDownWidget):
    """裁剪工具控制 Widget，用于控制 CanvasCropTool 的参数"""
    
    # 信号：取消裁剪
    crop_cancelled = Signal()
    # 信号：应用裁剪
    crop_applied = Signal()
    
    # 预设的长宽比
    ASPECT_RATIOS = {
        "自由比例": None,
        "1:1 (正方形)": 1.0,
        "4:3 (标准)": 4.0 / 3.0,
        "16:9 (宽屏)": 16.0 / 9.0,
        "3:2 (相机)": 3.0 / 2.0,
        "黄金比例": 1.618,
    }
    
    def __init__(self, canvas, parent=None):
        super().__init__("裁剪工具", parent)
        self.canvas = canvas
        self.crop_tool = canvas.crop_tool if canvas else None
        
        # 状态变量
        self._updating_from_crop = False  # 防止循环更新
        self._lock_aspect_ratio = False   # 是否锁定长宽比
        self._current_aspect = None       # 当前锁定的长宽比
        
        # 连接 crop_tool 的信号
        if self.crop_tool:
            self.crop_tool.cropbox_changed.connect(self._on_cropbox_changed)
        
        self.setContentBuilder(self._build_content_widget)
        self.setMinimumWidth(200)
    
    def _build_content_widget(self):
        """构建内容区域"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        # === 尺寸显示区域 ===
        size_group = self._create_size_group()
        content_layout.addWidget(size_group)
        
        # === 预设比例下拉菜单 ===
        aspect_group = self._create_aspect_group()
        content_layout.addWidget(aspect_group)
        
        # === 维持长宽比 Checkbox ===
        self._lock_ratio_checkbox = QCheckBox("维持长宽比例")
        self._lock_ratio_checkbox.stateChanged.connect(self._on_lock_ratio_changed)
        content_layout.addWidget(self._lock_ratio_checkbox)
        
        # === 按钮区域 ===
        button_group = self._create_button_group()
        content_layout.addWidget(button_group)
        
        # 初始更新尺寸显示
        self._update_size_display()
        
        return content_widget
    
    def _create_size_group(self):
        """创建尺寸显示和编辑区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # 宽度输入行
        width_layout = QHBoxLayout()
        width_layout.setSpacing(3)
        width_label = QLabel("宽:")
        width_label.setFixedWidth(30)
        self._width_spinbox = QDoubleSpinBox()
        self._width_spinbox.setRange(0.001, 1e6)
        self._width_spinbox.setDecimals(3)
        self._width_spinbox.setSingleStep(0.1)
        self._width_spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._width_spinbox.valueChanged.connect(self._on_width_changed)
        width_layout.addWidget(width_label)
        width_layout.addWidget(self._width_spinbox)
        
        # 高度输入行
        height_layout = QHBoxLayout()
        height_layout.setSpacing(3)
        height_label = QLabel("高:")
        height_label.setFixedWidth(30)
        self._height_spinbox = QDoubleSpinBox()
        self._height_spinbox.setRange(0.001, 1e6)
        self._height_spinbox.setDecimals(3)
        self._height_spinbox.setSingleStep(0.1)
        self._height_spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._height_spinbox.valueChanged.connect(self._on_height_changed)
        height_layout.addWidget(height_label)
        height_layout.addWidget(self._height_spinbox)
        
        layout.addLayout(width_layout)
        layout.addLayout(height_layout)
        
        return widget
    
    def _create_aspect_group(self):
        """创建预设比例下拉菜单"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        label = QLabel("预设:")
        label.setFixedWidth(30)
        
        self._aspect_combo = QComboBox()
        self._aspect_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._aspect_combo.setMaximumWidth(140)
        for ratio_name in self.ASPECT_RATIOS.keys():
            self._aspect_combo.addItem(ratio_name)
        self._aspect_combo.currentTextChanged.connect(self._on_aspect_ratio_changed)
        
        layout.addWidget(label)
        layout.addWidget(self._aspect_combo)
        
        return widget
    
    def _create_button_group(self):
        """创建确定/取消按钮区域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 取消按钮
        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.setMaximumWidth(80)
        self._cancel_btn.clicked.connect(self._on_cancel_crop)
        
        # 确定按钮
        self._apply_btn = QPushButton("确定")
        self._apply_btn.setMaximumWidth(80)
        self._apply_btn.clicked.connect(self._on_apply_crop)
        
        layout.addWidget(self._cancel_btn)
        layout.addWidget(self._apply_btn)
        
        return widget
    
    def _update_size_display(self):
        """更新尺寸显示（响应 cropbox 变化）"""
        if self._updating_from_crop or not self.crop_tool:
            return
        
        # 检查是否已经构建了内容（widget 是否已展开）
        if not hasattr(self, '_width_spinbox') or not hasattr(self, '_height_spinbox'):
            return
        
        self._updating_from_crop = True
        try:
            x0, y0, x1, y1 = self.crop_tool.get_crop_bounds()
            width = abs(x1 - x0)
            height = abs(y1 - y0)
            
            # 更新输入框的值
            self._width_spinbox.blockSignals(True)
            self._height_spinbox.blockSignals(True)
            self._width_spinbox.setValue(width)
            self._height_spinbox.setValue(height)
            self._width_spinbox.blockSignals(False)
            self._height_spinbox.blockSignals(False)
        finally:
            self._updating_from_crop = False
    
    def _on_width_changed(self, new_width):
        """宽度改变时的处理"""
        if self._updating_from_crop or not self.crop_tool:
            return
        
        self._updating_from_crop = True
        try:
            x0, y0, x1, y1 = self.crop_tool.get_crop_bounds()
            
            # 保持左下角不变，调整右上角
            new_x1 = x0 + new_width
            
            # 如果锁定比例，同时调整高度
            if self._lock_aspect_ratio and self._current_aspect is not None:
                new_height = new_width / self._current_aspect
                self.crop_tool._y1 = y0 + new_height
            
            self.crop_tool._x1 = new_x1
            self.crop_tool._update_crop_box()
        finally:
            self._updating_from_crop = False
    
    def _on_height_changed(self, new_height):
        """高度改变时的处理"""
        if self._updating_from_crop or not self.crop_tool:
            return
        
        self._updating_from_crop = True
        try:
            x0, y0, x1, y1 = self.crop_tool.get_crop_bounds()
            
            # 保持左下角不变，调整右上角
            new_y1 = y0 + new_height
            
            # 如果锁定比例，同时调整宽度
            if self._lock_aspect_ratio and self._current_aspect is not None:
                new_width = new_height * self._current_aspect
                self.crop_tool._x1 = x0 + new_width
            
            self.crop_tool._y1 = new_y1
            self.crop_tool._update_crop_box()
        finally:
            self._updating_from_crop = False
    
    def _on_aspect_ratio_changed(self, ratio_name):
        """预设比例改变时的处理"""
        aspect = self.ASPECT_RATIOS.get(ratio_name)
        self._current_aspect = aspect
        
        # 如果选择了非自由比例，自动启用锁定
        if aspect is not None:
            self._lock_aspect_ratio = True
            self._lock_ratio_checkbox.setChecked(True)
            
            # 根据当前宽度应用新比例
            if self.crop_tool:
                x0, y0, x1, y1 = self.crop_tool.get_crop_bounds()
                width = abs(x1 - x0)
                new_height = width / aspect
                self.crop_tool._y1 = y0 + new_height
                self.crop_tool._update_crop_box()
                self._update_size_display()
        else:
            self._lock_aspect_ratio = False
            self._lock_ratio_checkbox.setChecked(False)
    
    def _on_lock_ratio_changed(self, state):
        """维持长宽比 Checkbox 改变时的处理"""
        self._lock_aspect_ratio = (state == Qt.Checked)
        
        # 如果启用锁定，更新当前比例
        if self._lock_aspect_ratio and self.crop_tool:
            x0, y0, x1, y1 = self.crop_tool.get_crop_bounds()
            width = abs(x1 - x0)
            height = abs(y1 - y0)
            if height > 0:
                self._current_aspect = width / height
                # 更新下拉菜单到最接近的预设
                self._update_combo_to_current_aspect()
    
    def _update_combo_to_current_aspect(self):
        """根据当前比例更新下拉菜单选择"""
        if self._current_aspect is None:
            return
        
        # 找到最接近的预设
        min_diff = float('inf')
        closest_name = "自由比例"
        
        for name, aspect in self.ASPECT_RATIOS.items():
            if aspect is not None:
                diff = abs(aspect - self._current_aspect)
                if diff < min_diff:
                    min_diff = diff
                    closest_name = name
        
        # 如果差异很小，选择对应的预设
        if min_diff < 0.05:  # 5% 的容差
            self._aspect_combo.blockSignals(True)
            self._aspect_combo.setCurrentText(closest_name)
            self._aspect_combo.blockSignals(False)
    
    def _on_apply_crop(self):
        """应用裁剪"""
        if self.crop_tool and self.crop_tool.is_active():
            self.crop_tool.apply_crop()
            # 发出信号通知父组件
            self.crop_applied.emit()
    
    def _on_cancel_crop(self):
        """取消裁剪 - 发出信号通知父组件"""
        self.crop_cancelled.emit()
    
    def _on_cropbox_changed(self, x0, y0, x1, y1):
        """当 cropbox 变化时更新显示"""
        self._update_size_display()
    
    def set_crop_tool(self, crop_tool: CanvasCropTool):
        """设置关联的 CanvasCropTool"""
        self.crop_tool = crop_tool
        if self.crop_tool:
            self._update_size_display()
    
    def refresh_size_display(self):
        """外部调用的刷新尺寸显示方法"""
        self._update_size_display()
    
    def sizeHint(self):
        if self.isCollapsed():
            return QSize(200, 24)
        return QSize(200, 180)
