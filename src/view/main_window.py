import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QTreeView,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle,
    QLabel, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel
from model.matplot_canvas import MatplotCanvas
from model.table_model import TableModel
from controller.property_controller import PropertyController
# from view.view import View


class MainWindow(QMainWindow):
    def __init__(self, model=None, parent=None):
        super().__init__()
        self.canvas = MatplotCanvas(self, width=5, height=4, dpi=100)
        self._init_window(model)

    def _init_window(self, model):
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

        self.tree_panel = TreePanel(model)
        node = model.getItem(QModelIndex())
        self.property_panel = PropertyPanel(TableModel(node))

        self.controller = PropertyController(self.tree_panel, self.property_panel)
        # self.tree_panel.item_selected.connect(self.property_panel.refresh_panel)
        # self.tree_panel.item_selected.connect(self.property_panel.refresh_panel_path)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.tree_panel)
        left_splitter.addWidget(self.property_panel)
        left_splitter.setSizes([300, 250])
        left_layout.addWidget(left_splitter)

        # 创建分割器
        splitter = QSplitter()

        splitter.addWidget(left_splitter)

        tab_widget = QTabWidget()
        tab_widget.addTab(self.canvas, "Plot")
        tab_widget.addTab(QWidget(), "Table")
        splitter.addWidget(tab_widget)
        splitter.setSizes([250, 750])
        hlayout.addWidget(splitter)

        # 初始绘图
        # pm.update_canvas("plot_1")