from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PySide6.QtCore import Signal
# from delegate.delegate import TaskDelegate

# from controller.controller import TaskController  # 如需使用可取消注释
class TreePanel(QWidget):
    nodeSelected = Signal(object)  # 发出选中的节点对象

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        self.tree_view.clicked.connect(self.on_item_clicked)
    
    def on_item_clicked(self, index):
        node = self.model.getItem(index)
        # 发出信号或调用回调以通知选择了新节点
        self.nodeSelected.emit(node)
        

class TreeWindow(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Panel Example")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        self.tree_panel = TreePanel(model)
        self.layout.addWidget(self.tree_panel)

        self.setLayout(self.layout)

