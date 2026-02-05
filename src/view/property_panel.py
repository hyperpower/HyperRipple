from PySide6.QtWidgets import QWidget, QVBoxLayout, QListView
# from delegate.delegate import TaskDelegate



class PropertyPanel(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.list_view = QListView()
        self.list_view.setModel(self.model)
        # self.tree_view.setItemDelegate(TaskDelegate())
        # self.tree_view.setSpacing(4)
        # self.tree_view.setUniformItemSizes(False)
        # Controller
        # self.controller = TaskController(self.model, self.tree_view)
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_view)
        self.setLayout(layout)
