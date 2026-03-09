from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QMenu
from PySide6.QtCore import Signal, Qt, Slot

from controller.tree_controller import TreePanelController
from view.view_helper import *

class TreePanel(QWidget):
    nodeSelected = Signal(object)  # 发出选中的节点对象
    requestBuildContextMenu = Signal(object, object)  # 发出请求构建右键菜单的信号
    nodeDoubleClicked = Signal(object)  # 可供外部连接

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
        self.tree_view.doubleClicked.connect(self._on_double_clicked)

        # 右键菜单
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._on_context_menu)

        self.context_menu_controller = TreePanelController(self)

        # 默认展开第一层级
        self.tree_view.expandToDepth(1)

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
        empty_icon = createEmptyIcon()
        icon_expand = createThemedIcon("asset/icons/list_down.svg")
        icon_collapse = createThemedIcon("asset/icons/list_up.svg")

        if not index.isValid():
            menu.addAction(icon_expand, "Expand All", self.tree_view.expandAll)
            menu.addAction(icon_collapse, "Collapse All", self.tree_view.collapseAll)
        else: # valid index
            self.requestBuildContextMenu.emit(menu, index)
            menu.addSeparator()
            menu.addAction(icon_expand, "Expand", lambda: self.tree_view.expand(index))
            menu.addAction(empty_icon, "Expand All", self.tree_view.expandAll)
            menu.addAction(icon_collapse, "Collapse", lambda: self.tree_view.collapse(index)) 
            menu.addAction(empty_icon, "Collapse All", self.tree_view.collapseAll)
            menu.addSeparator()
        return menu

    @Slot('QModelIndex')
    def _on_double_clicked(self, index):
        if not index.isValid():
            return
        node = index.internalPointer() if hasattr(index, "internalPointer") else None
        if node and hasattr(node, "openRequested"):
            # 如果节点有 openRequested 信号，直接发出
            node.openRequested.emit(node)
        else:
            # 否则发出自定义信号，由 controller 处理
            self.nodeDoubleClicked.emit(node)

class TreeWindow(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tree Panel Example")
        self.resize(400, 300)

        self.layout = QVBoxLayout(self)

        self.tree_panel = TreePanel(model)
        self.layout.addWidget(self.tree_panel)

        self.setLayout(self.layout)

