from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView, QAbstractItemView
from delegate.property_delegate import PropertyDelegate



 
class PropertyPanel(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(PropertyDelegate(self.view))  # 设置自定义delegate

        header = self.view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  
        header.setSectionResizeMode(1, QHeaderView.Stretch)      
        header.setSectionsMovable(False)                         
        header.setSectionsClickable(False)                       

        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)

        # 允许编辑
        self.view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)
    
    def setNode(self, node):
        self.model.setNode(node)
