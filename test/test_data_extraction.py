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

# from controller.property_controller import PropertyController
from view.tree_panel import TreePanel
from view.property_panel import PropertyPanel 
from model.matplot_model import MatplotModel
from model.tree_model import TreeModel
# from model.matplot_node import MatplotNode
from model.table_model import TableModel
# from view.main_window import MainWindow
from view.de_window import DataExtractionWindow
from data_extraction.deta_extraction_node import DataExtractionRootNode, DataExtractionNode


def predefined_matplot_node():
    node =  DataExtractionNode("Data Extraction")
    return node



if __name__ == "__main__":
    print("Current working directory:", 
          os.getcwd())
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")

    
    # window = TreePropertyWindow(MatplotModel())
    mnode = predefined_matplot_node() 
    window = DataExtractionWindow(mnode)
    window.show()
    window.load_image_from_path("asset/test/coordinate_example.png")
    # window.main_node.new_figure("Figure 1")
    sys.exit(app.exec())