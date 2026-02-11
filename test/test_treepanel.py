import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QTextOption
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# ...existing code...delegate.delegate import TaskDelegate
# from view.view import View

from controller.property_controller import PropertyController
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel 
from model.matplot_model import MatplotModel
from model.tree_model import TreeModel
from model.matplot_node import MatplotNode
from model.table_model import TableModel
from view.main_window import MainWindow

class TreePropertyWindow(QMainWindow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Property Panel")
        self.resize(400, 300)

        central_widget = QWidget(self)
        self.layout = QVBoxLayout(central_widget)

        self.tree_panel = TreePanel(model)
        node = model.getItem(QModelIndex())
        self.property_panel = PropertyPanel(TableModel(node))
        self.layout.addWidget(self.tree_panel)
        self.layout.addWidget(self.property_panel)

        self.setCentralWidget(central_widget)

        self.controller = PropertyController(self.tree_panel, self.property_panel)

def predefined_matplot_node():
    matplot_node = MatplotNode("Plot")
    matplot_node.new_figure("Figure 1")
    matplot_node.new_figure("Figure 2")

    return matplot_node



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    screen = app.primaryScreen()

    print(f"屏幕名称: {screen.name()}")
    print(f"逻辑 DPI: {screen.logicalDotsPerInch()}") # 系统缩放后的 DPI (常用)
    print(f"物理 DPI: {screen.physicalDotsPerInch()}") # 硬件真实的 DPI
    print(f"设备像素比 (DPR): {screen.devicePixelRatio()}") # 缩放倍数，如 1.25, 2.0
    # window = TreePropertyWindow(MatplotModel())
    mnode = predefined_matplot_node() 
    window = MainWindow(mnode)
    window.show()
    # window.main_node.new_figure("Figure 1")
    sys.exit(app.exec())