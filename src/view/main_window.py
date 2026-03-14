import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QTreeView,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle,
    QLabel, QSplitter, QTabWidget, QProxyStyle, QDockWidget, QToolBar
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
from view.tab_panel import TabPanel
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel
from view.matplot_canvas import MatplotCanvas
from model.table_model import TableModel
from model.tree_model import TreeModel
# from controller.property_controller import PropertyController
from controller.main_controller import MainWindowController

class LeftAlignedTabStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_TabBar_Alignment:
            return Qt.AlignLeft
        return super().styleHint(hint, option, widget, returnData)

class MainWindow(QMainWindow):
    def __init__(self, node=None, parent=None):
        super().__init__()
        self.main_node = node
        self._init_window(node)
        self.controller = MainWindowController(self)

    def _init_window(self, node):
        self.setWindowTitle("PyQt Matplotlib")
        self.setGeometry(350, 350, 800, 600)
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
        self.tab_panel = TabPanel()
        splitter = QSplitter()
        splitter.addWidget(self.tab_panel)
        splitter.setSizes([250, 750])
        hlayout.addWidget(splitter)
        self.tree_dock = QDockWidget("操作面板", self)
        self.tree_dock.setWidget(left_splitter)
        self.tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree_dock)
        self.left_toolbar = QToolBar("工具栏", self)
        self.left_toolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        tree_toggle_action = self.tree_dock.toggleViewAction()
        tree_toggle_action.setText("树面板")
        self.left_toolbar.addAction(tree_toggle_action)

    def on_action_requested(self, node, action_name):
        """
        响应 InputImageNode 的 actionRequested 信号，处理 'load' 和 'crop' 操作。
        """
        if action_name == "load":
            self.on_load_image_requested(node)
        elif action_name == "crop":
            self.on_crop_image_requested(node)