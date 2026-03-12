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
        # self.canvas = MatplotCanvas(self, width=5, height=4, dpi=100)
        # self.canvas = []
        self.main_node = node
        self._init_window(node)

        # for test
        # self._load_test_fig("coordinate_example.png")
        
        self.zoom_widget._toggle_dropdown()  # 默认展开放大镜工具
        # self.manual_extraction_widget.setCollapsed(False)  # 默认展开手动提取工具
        self.manual_extraction_widget._toggle_dropdown()  # 默认展开手动提取工具

        self.controller = DEMainWindowController(self, self.main_node)

        

    def _init_window(self, node):
        self.setWindowTitle("PyQt Matplotlib")
        self.setGeometry(300, 350, 1100, 600)

        # 创建一个主控件和布局
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)

        #left layout
        left_layout = QVBoxLayout() 
        hlayout.addLayout(left_layout)

        # Stuatus bar 
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
        # CropToolWidget - 只在 crop 模式激活时添加到 right_dock
        self.crop_tool_widget = CropToolWidget(self.canvas)
        self.canvas.crop_tool.crop_completed.connect(self.on_crop_completed)
        self.canvas.crop_tool.cropbox_changed.connect(self._on_cropbox_changed)
        
        # 连接 CropToolWidget 的信号
        self.crop_tool_widget.crop_cancelled.connect(self._on_crop_cancelled)
        self.crop_tool_widget.crop_applied.connect(self._on_crop_applied)
        self._crop_mode = False
        self._original_image = None  # 保存原始图像用于裁剪
        # self.manual_extraction_widget._build_content_widget()

        splitter = QSplitter()
        splitter.addWidget(self.fig_panel)
        splitter.setSizes([250, 750])
        splitter.setContentsMargins(0, 0, 0, 0)
        hlayout.addWidget(splitter, stretch=1)

        # 创建 tree_panel 的 dock
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
        # CropToolWidget 初始不添加，只有在 crop 模式激活时才添加
        self._crop_tool_widget_added = False
        right_layout.addStretch(1)
        self.right_dock.setWidget(right_container)
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        # 左侧竖向工具栏
        self.left_toolbar = QToolBar("工具栏", self)
        self.left_toolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)

        tree_toggle_action = self.tree_dock.toggleViewAction()
        tree_toggle_action.setText("树面板")
        self.left_toolbar.addAction(tree_toggle_action)
    
    def on_load_image_requested(self, node):
        # print(f"DataExtractionWindow: Received load image request from node {node.name}.")
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
        node["path"].value = file_path  # Update the node's path property
        imge, width, height = self.load_image_from_path(file_path)
        node.set_image(imge)  # Store the loaded image in the node
        node["image_width"].value = width
        node["image_height"].value = height
    
    def _load_test_fig(self, fn):
        fig = self.canvas.figure
        fig.clear()

        image_path = os.path.join("asset", "test", fn)
        image = mpimg.imread(image_path)
        height, width = image.shape[:2]
        

        self.canvas.axes = fig.add_subplot(111)
        self.canvas.axes.imshow(image)
        fig.tight_layout(pad=0)
        self.canvas.draw_idle()

    
    def on_crop_completed(self, x0, y0, x1, y1):
        """处理裁剪完成事件 - 由 crop_tool.crop_completed 信号触发"""
        if self._original_image is None:
            return
        
        # 获取当前显示的图像范围
        ax = self.canvas.main_ax
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # 获取图像尺寸
        img_height, img_width = self._original_image.shape[:2]
        
        # 计算数据坐标到图像像素坐标的映射
        # 数据坐标 (xlim[0], xlim[1]) 对应图像 (0, img_width)
        # 数据坐标 (ylim[0], ylim[1]) 对应图像 (img_height, 0) (因为图像 y 轴向下)
        
        # 计算裁剪区域在图像中的像素坐标
        x_ratio = img_width / (xlim[1] - xlim[0]) if xlim[1] != xlim[0] else 0
        y_ratio = img_height / (ylim[1] - ylim[0]) if ylim[1] != ylim[0] else 0
        
        # 处理反向坐标轴
        if xlim[0] > xlim[1]:
            x_ratio = -x_ratio
        if ylim[0] > ylim[1]:
            y_ratio = -y_ratio
        
        # 计算像素坐标（考虑图像坐标系 y 轴向下）
        px0 = int(max(0, min(img_width, (x0 - xlim[0]) * x_ratio)))
        px1 = int(max(0, min(img_width, (x1 - xlim[0]) * x_ratio)))
        py0 = int(max(0, min(img_height, (y0 - ylim[0]) * y_ratio)))
        py1 = int(max(0, min(img_height, (y1 - ylim[0]) * y_ratio)))
        
        # 确保坐标有序
        x_start, x_end = min(px0, px1), max(px0, px1)
        y_start, y_end = min(py0, py1), max(py0, py1)
        
        # 执行裁剪
        cropped_image = self._original_image[y_start:y_end, x_start:x_end]
        
        # 显示裁剪后的图像
        self._display_cropped_image(cropped_image)
        
        # 退出裁剪模式
        self.set_crop_mode(False)
        self.canvas.set_mode(None)
        self.canvas.crop_tool.set_active(False)
        self.manual_extraction_widget.set_crop_mode(False)
    
    def _display_cropped_image(self, cropped_image):
        """显示裁剪后的图像"""
        if cropped_image.size == 0:
            QMessageBox.warning(self, "警告", "裁剪区域为空")
            return
        
        self.canvas.main_ax.clear()
        self.canvas.main_ax.imshow(cropped_image)
        self.canvas.draw_idle()
        
        # 更新原始图像引用
        self._original_image = cropped_image
    
    def set_crop_mode(self, active: bool):
        """设置裁剪模式 - 控制 CropToolWidget 的显示"""
        self._crop_mode = active
        
        right_container = self.right_dock.widget()
        right_layout = right_container.layout()
        
        if active:
            # 激活 crop 模式，添加 CropToolWidget
            if not self._crop_tool_widget_added:
                # 在 manual_extraction_widget 之后，stretch 之前添加
                right_layout.insertWidget(right_layout.count() - 1, self.crop_tool_widget)
                self._crop_tool_widget_added = True
            self.crop_tool_widget.setCollapsed(False)
            # 设置 canvas 的 crop 模式
            self.canvas.set_mode('crop')
            self.canvas.crop_tool.set_active(True)
        else:
            # 退出 crop 模式，移除 CropToolWidget
            print("Exiting crop mode, removing CropToolWidget if added")
            print("active:", active, "crop_tool_widget_added:", self._crop_tool_widget_added)
            if self._crop_tool_widget_added:
                right_layout.removeWidget(self.crop_tool_widget)
                self.crop_tool_widget.setParent(None)
                self._crop_tool_widget_added = False
            # 清除 canvas 的 crop 模式
            self.canvas.set_mode(None)
            self.canvas.crop_tool.set_active(False)
            
            # 取消工具栏 crop 按钮的选中状态
            self._unset_toolbar_crop_button()
    
    def _unset_toolbar_crop_button(self):
        """取消工具栏 crop 按钮的选中状态"""
        if hasattr(self.fig_panel, 'toolbar') and hasattr(self.fig_panel.toolbar, 'actions'):
            if 'crop' in self.fig_panel.toolbar.actions:
                self.fig_panel.toolbar.actions['crop'].setChecked(False)
    
    def _on_cropbox_changed(self, x0, y0, x1, y1):
        """当 cropbox 变化时，确保 CropToolWidget 被添加"""
        if self._crop_mode and not self._crop_tool_widget_added:
            right_container = self.right_dock.widget()
            right_layout = right_container.layout()
            right_layout.insertWidget(right_layout.count() - 1, self.crop_tool_widget)
            self._crop_tool_widget_added = True
            self.crop_tool_widget.setCollapsed(False)
    
    def _on_crop_cancelled(self):
        """处理 CropToolWidget 取消裁剪信号"""
        self.set_crop_mode(False)
    
    def _on_crop_applied(self):
        """处理 CropToolWidget 应用裁剪信号"""
        self.set_crop_mode(False)
    
    def load_image_from_path(self, file_path):
        """加载图像并保存原始图像用于后续裁剪"""
        if not file_path:
            return None
        image = mpimg.imread(file_path)
        height, width = image.shape[:2]
        self._original_image = image  # 保存原始图像
        self.canvas.main_ax.clear()
        self.canvas.main_ax.imshow(image)
        # 设置初始视图范围（在显示图片后）
        self.canvas.set_initial_view()
        self.canvas.draw_idle()
        return image, width, height


        
