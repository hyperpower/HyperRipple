from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSplitter, QDockWidget, QToolBar
)
from PySide6.QtCore import Qt

from model.tree_model import TreeModel
from model.table_model import TableModel
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel
from view.fig_panel import FigPanel
from view.matplot_canvas import MatplotCanvas


class DataExtractionWindow(QMainWindow):
    def __init__(self, node=None, parent=None):
        super().__init__()
        # self.canvas = MatplotCanvas(self, width=5, height=4, dpi=100)
        # self.canvas = []
        self.main_node = node
        self._init_window(node)

        # self.controller = MainWindowController(self)

        

    def _init_window(self, node):
        self.setWindowTitle("PyQt Matplotlib")
        self.setGeometry(350, 350, 800, 600)

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

        # form_btn = QPushButton("打开表单窗口")
        # form_btn.clicked.connect(self.show_form)
        # layout.addWidget(form_btn)

        tree_model = TreeModel(node)
        self.tree_panel = TreePanel(tree_model)
        # node = self.tree_panel.getItem(QModelIndex())
        table_model = TableModel(node)
        self.property_panel = PropertyPanel(table_model)


        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.tree_panel)
        left_splitter.addWidget(self.property_panel)
        left_splitter.setSizes([300, 250])

        self.canvas = MatplotCanvas(None)
        self.fig_panel = FigPanel(self.canvas)
        
        splitter = QSplitter()
        splitter.addWidget(self.fig_panel)
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