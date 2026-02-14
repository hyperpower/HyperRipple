from PySide6.QtCore import QObject

from view.view_helper import createEmptyIcon, createThemedIcon


class TreePanelController(QObject):
    def __init__(self, tree_panel):
        super().__init__()
        self.tree_panel = tree_panel
        self.tree_panel.requestBuildContextMenu.connect(self._on_build_context_menu)
        self._listened_nodes = set()

    def _on_build_context_menu(self, menu, index):
        node = self.tree_panel.model.getItem(index)
        # 监听 node 的 dataChanged 信号
        if id(node) not in self._listened_nodes:
            node.dataChanged.connect(self._on_node_data_changed)
            node.layoutChanged.connect(self._on_node_layout_changed)
            self._listened_nodes.add(id(node))
        actions = node.allowed_actions() 
        print(f"Building context menu for node: {node.name}, actions: {actions}")
        if actions:
            for icon_name, action_name, handler in actions:
                if icon_name:
                    icon = createThemedIcon(f"asset/icons/{icon_name}")
                else:
                    icon = createEmptyIcon()
                menu.addAction(icon, action_name, lambda checked=False, h=handler: h())

    def _on_node_data_changed(self, node, role):
        print(f"Node data changed: {node.name}, role: {role}")
        # 这里可以添加刷新视图或其他逻辑

    def _on_node_layout_changed(self, node):
        model = self.tree_panel.model
        index = model.index_from_node(node)
        
        model.layoutChanged.emit()

        if not self.tree_panel.tree_view.isExpanded(index):
            self.tree_panel.tree_view.expand(index)
        # 这里可以添加刷新视图或其他逻辑

    def id_to_function_name(self, name):
        name = name.replace("...", "")
        name = name.strip()
        return name.replace(" ", "_").lower()

