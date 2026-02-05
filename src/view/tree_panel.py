from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView
# from delegate.delegate import TaskDelegate

# from controller.controller import TaskController  # 如需使用可取消注释
class TreePanel(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)
        

class TreeWindow(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Panel Example")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        self.tree_panel = TreePanel(model)
        self.layout.addWidget(self.tree_panel)

        self.setLayout(self.layout)

