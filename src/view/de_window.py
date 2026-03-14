import os

import matplotlib.image as mpimg
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QDockWidget, QToolBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

from controller.de_window_controller import DEMainWindowController
from model.tree_model import TreeModel
from model.table_model import TableModel
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel
from view.fig_panel import FigPanel
from view.matplot_canvas import MatplotCanvas
from view.zoom_widget import ZoomWidget
from view.manual_extraction_widget import ManualExtractionWidget
from view.crop_tool_widget import CropToolWidget

class DataExtractionWindow(QMainWindow):
    def __init__(self, node=None, parent=None):
        super().__init__()
        self.main_node = node
        self._init_window(node)

        self.zoom_widget._toggle_dropdown()  # 默认展开放大镜工具
        self.manual_extraction_widget._toggle_dropdown()  # 默认展开手动提取工具

        self.controller = DEMainWindowController(self, self.main_node)

    def _init_window(self, node):
        self.setWindowTitle("PyQt Matplotlib")
        self.setGeometry(300, 350, 1100, 600)
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)
        left_layout = QVBoxLayout() 
        hlayout.addLayout(left_layout)
        label = QLabel("状态栏")
        self.statusBar().addWidget(label)
        tree_model = TreeModel(node)
        self.tree_panel = TreePanel(tree_model)
        table_model = TableModel(node)
        self.property_panel = PropertyPanel(table_model)
        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.tree_panel)
        left_splitter.addWidget(self.property_panel)
        left_splitter.setSizes([300, 250])
        left_splitter.setContentsMargins(0, 0, 0, 0)
        self.canvas = MatplotCanvas(None, node._main_fig)
        self.fig_panel = FigPanel(self.canvas)
        self.zoom_widget = ZoomWidget(self.canvas)
        self.zoom_canvas = self.zoom_widget.zoom_canvas
        self.manual_extraction_widget = ManualExtractionWidget()
        self.crop_tool_widget = CropToolWidget(self.canvas)
        self.canvas.crop_tool.crop_completed.connect(self.on_crop_completed)
        self.canvas.crop_tool.cropbox_changed.connect(self._on_cropbox_changed)
        self.crop_tool_widget.crop_cancelled.connect(self._on_crop_cancelled)
        self.crop_tool_widget.crop_applied.connect(self._on_crop_applied)
        self._crop_mode = False
        self._original_image = None
        splitter = QSplitter()
        splitter.addWidget(self.fig_panel)
        splitter.setSizes([250, 750])
        splitter.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(splitter, stretch=1)
        self.tree_dock = QDockWidget("数据面板", self)
        self.tree_dock.setWidget(left_splitter)
        self.tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree_dock)
        self.right_dock = QDockWidget("工作面板", self)
        self.right_dock.setFeatures(QDockWidget.DockWidgetMovable)
        right_container = QWidget(self.right_dock)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.zoom_widget)
        right_layout.addWidget(self.manual_extraction_widget)
        self.crop_tool_widget = CropToolWidget(self.canvas)
        self._crop_tool_widget_added = False
        right_layout.addStretch(1)
        self.right_dock.setWidget(right_container)
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
        self.left_toolbar = QToolBar("工具栏", self)
        self.left_toolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        tree_toggle_action = self.tree_dock.toggleViewAction()
        tree_toggle_action.setText("树面板")
        self.left_toolbar.addAction(tree_toggle_action)
    
    def on_load_image_requested(self, node):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp);;All Files (*)"
        )
        if not file_path:
            return None
        if node.get_class_name() != "InputImageNode":
            return None
        node.load_image_from_path(file_path)
        self.draw_image_on_canvas(node)

    def draw_image_on_canvas(self, node):
        self.canvas.main_ax.clear()
        self.canvas.main_ax.imshow(node._image)
        self.canvas.set_initial_view()
        self.canvas.draw_idle()
    
    def on_crop_completed(self, x0, y0, x1, y1):
        if self._original_image is None:
            return
        ax = self.canvas.main_ax
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        img_height, img_width = self._original_image.shape[:2]
        x_ratio = img_width / (xlim[1] - xlim[0]) if xlim[1] != xlim[0] else 0
        y_ratio = img_height / (ylim[1] - ylim[0]) if ylim[1] != ylim[0] else 0
        if xlim[0] > xlim[1]:
            x_ratio = -x_ratio
        if ylim[0] > ylim[1]:
            y_ratio = -y_ratio
        px0 = int(max(0, min(img_width, (x0 - xlim[0]) * x_ratio)))
        px1 = int(max(0, min(img_width, (x1 - xlim[0]) * x_ratio)))
        py0 = int(max(0, min(img_height, (y0 - ylim[0]) * y_ratio)))
        py1 = int(max(0, min(img_height, (y1 - ylim[0]) * y_ratio)))
        x_start, x_end = min(px0, px1), max(px0, px1)
        y_start, y_end = min(py0, py1), max(py0, py1)
        cropped_image = self._original_image[y_start:y_end, x_start:x_end]
        self._display_cropped_image(cropped_image)
        self.set_crop_mode(False)
        self.canvas.set_mode(None)
        self.canvas.crop_tool.set_active(False)
        self.manual_extraction_widget.set_crop_mode(False)
    
    def _display_cropped_image(self, cropped_image):
        if cropped_image.size == 0:
            QMessageBox.warning(self, "警告", "裁剪区域为空")
            return
        self.canvas.main_ax.clear()
        self.canvas.main_ax.imshow(cropped_image)
        self.canvas.draw_idle()
        self._original_image = cropped_image
    
    def set_crop_mode(self, active: bool):
        self._crop_mode = active
        right_container = self.right_dock.widget()
        right_layout = right_container.layout()
        if active:
            if not self._crop_tool_widget_added:
                right_layout.insertWidget(right_layout.count() - 1, self.crop_tool_widget)
                self._crop_tool_widget_added = True
            self.crop_tool_widget.setCollapsed(False)
            self.canvas.set_mode('crop')
            self.canvas.crop_tool.set_active(True)
        else:
            if self._crop_tool_widget_added:
                right_layout.removeWidget(self.crop_tool_widget)
                self.crop_tool_widget.setParent(None)
                self._crop_tool_widget_added = False
            self.canvas.set_mode(None)
            self.canvas.crop_tool.set_active(False)
            self._unset_toolbar_crop_button()
    
    def _unset_toolbar_crop_button(self):
        if hasattr(self.fig_panel, 'toolbar') and hasattr(self.fig_panel.toolbar, '_actions'):
            if 'crop' in self.fig_panel.toolbar._actions:
                self.fig_panel.toolbar._actions['crop'].setChecked(False)
    
    def _on_cropbox_changed(self, x0, y0, x1, y1):
        if self._crop_mode and not self._crop_tool_widget_added:
            right_container = self.right_dock.widget()
            right_layout = right_container.layout()
            right_layout.insertWidget(right_layout.count() - 1, self.crop_tool_widget)
            self._crop_tool_widget_added = True
            self.crop_tool_widget.setCollapsed(False)
    
    def _on_crop_cancelled(self):
        self.set_crop_mode(False)
    
    def _on_crop_applied(self):
        self.set_crop_mode(False)
    
    def on_action_requested(self, node, action_name):
        """
        响应 InputImageNode 的 actionRequested 信号，处理 'load' 和 'crop' 操作。
        """
        if action_name == "load":
            self.on_load_image_requested(node)
        elif action_name == "crop":
            self.on_crop_image_requested(node)

    def on_crop_image_requested(self, node):
        """
        响应 crop 操作请求，激活裁剪模式。
        """
        self.set_crop_mode(True)
