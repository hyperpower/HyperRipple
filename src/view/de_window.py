import os

import matplotlib.image as mpimg
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QDockWidget, QToolBar, QFileDialog
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
        node["image_width"].value = width
        node["image_height"].value = height
    
    def load_image_from_path(self, file_path):
        if not file_path:
            return None
        image = mpimg.imread(file_path)
        height, width = image.shape[:2]
        self.canvas.main_ax.clear()
        self.canvas.main_ax.imshow(image)
        self.canvas.draw_idle()
        return image, width, height

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


        
