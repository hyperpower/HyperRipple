import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QTreeView,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle,
    QLabel, QSplitter, QTabWidget, QProxyStyle, QDockWidget, QToolBar
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel
from view.matplot_canvas import MatplotCanvas
from model.table_model import TableModel
from model.tree_model import TreeModel
from controller.property_controller import PropertyController
from controller.matplot_controller import CanvasController
from controller.matplot_controller import MainWindowController
# from view.view import View


class LeftAlignedTabStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_TabBar_Alignment:
            return Qt.AlignLeft
        return super().styleHint(hint, option, widget, returnData)


class MainWindow(QMainWindow):
    def __init__(self, node=None, parent=None):
        super().__init__()
        # self.canvas = MatplotCanvas(self, width=5, height=4, dpi=100)
        # self.canvas = []
        self.main_node = node
        self._init_window(node)

        self.controller = MainWindowController(self)

    def _init_window(self, node):
        self.setWindowTitle("PyQt Matplotlib")
        self.setGeometry(350, 350, 1600, 1000)

        # 创建一个主控件和布局
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 创建一个绘图画布
        # pm = self.manager.managers["plots"]
        # self.canvas = pm.canvas["plot_1"]
        # toolbar = NavigationToolbar(self.canvas, self)
        # layout.addWidget(toolbar)
        # horizontal layout
        hlayout = QHBoxLayout()
        layout.addLayout(hlayout)

        #left layout
        left_layout = QVBoxLayout() 
        hlayout.addLayout(left_layout)

        # 示例按钮
        label = QLabel("状态栏")
        self.statusBar().addWidget(label)

        # form_btn = QPushButton("打开表单窗口")
        # form_btn.clicked.connect(self.show_form)
        # layout.addWidget(form_btn)

        tree_model = TreeModel(node)
        self.tree_panel = TreePanel(tree_model)
        # node = self.tree_panel.getItem(QModelIndex())
        table_model = TableModel(node)
        self.property_panel = PropertyPanel(table_model)

        self.controller = PropertyController(self.tree_panel, self.property_panel)
        # self.matplot_controller = CanvasController(table_model, self.canvas)
        # self.tree_panel.item_selected.connect(self.property_panel.refresh_panel)
        # self.tree_panel.item_selected.connect(self.property_panel.refresh_panel_path)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.tree_panel)
        left_splitter.addWidget(self.property_panel)
        left_splitter.setSizes([300, 250])
        # left_layout.addWidget(left_splitter)


        # splitter.addWidget(left_splitter)

        self.tab_widget = QTabWidget()
        

        self.tab_widget.setStyle(LeftAlignedTabStyle())
        

        splitter = QSplitter()
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([250, 750])
        hlayout.addWidget(splitter)

        # 创建 tree_panel 的 dock
        self.tree_dock = QDockWidget("操作面板", self)
        self.tree_dock.setWidget(left_splitter)
        self.tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree_dock)

        # 左侧竖向工具栏
        self.left_toolbar = QToolBar("工具栏", self)
        self.left_toolbar.setOrientation(Qt.Vertical)
        self.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)

        tree_toggle_action = self.tree_dock.toggleViewAction()
        tree_toggle_action.setText("树面板")
        self.left_toolbar.addAction(tree_toggle_action)


        # 你可以设置 dock 的初始大小和位置
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # 初始绘图
        # pm.update_canvas("plot_1")
    
    def add_new_figure_tab(self, canvas, title):
        self.tab_widget.addTab(canvas, title)
        self.tab_widget.setCurrentWidget(canvas)

        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(lambda i: self.tab_widget.removeTab(i))
        self.tab_widget.tabBar().setExpanding(False)
        self.tab_widget.tabBar().setUsesScrollButtons(True)
    
    
