from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QMenu
from PySide6.QtCore import Signal, Qt

from controller.tree_controller import TreePanelController

class TreePanel(QWidget):
    nodeSelected = Signal(object)  # 发出选中的节点对象
    requestBuildContextMenu = Signal(object, object)  # 发出请求构建右键菜单的信号

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.header().hide()

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

        # 左键点击
        self.tree_view.clicked.connect(self.on_item_clicked)

        # 右键菜单
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._on_context_menu)

        self.context_menu_controller = TreePanelController(self)

    def on_item_clicked(self, index):
        if not index.isValid():
            return
        node = self.model.getItem(index)
        self.nodeSelected.emit(node)

    def _on_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)

        menu = self._build_context_menu(index)

        chosen = menu.exec(self.tree_view.viewport().mapToGlobal(pos))
        if chosen is None:
            return
    
    def _build_context_menu(self, index):
        menu = QMenu(self.tree_view)

        if not index.isValid():
            menu.addAction("Expand All", self.tree_view.expandAll)
            menu.addAction("Collapse All", self.tree_view.collapseAll)
        else: # valid index
            self.requestBuildContextMenu.emit(menu, index)
            menu.addSeparator()
            menu.addAction("Expand", lambda: self.tree_view.expand(index))
            menu.addAction("Expand All", self.tree_view.expandAll)
            menu.addAction("Collapse", lambda: self.tree_view.collapse(index)) 
            menu.addAction("Collapse All", self.tree_view.collapseAll)
            menu.addSeparator()
        return menu

class TreeWindow(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Panel Example")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        self.tree_panel = TreePanel(model)
        self.layout.addWidget(self.tree_panel)

        self.setLayout(self.layout)

