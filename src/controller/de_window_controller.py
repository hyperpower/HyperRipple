from PySide6.QtCore import QObject, Signal


class DEMainWindowController(QObject):
    def __init__(self, main_window, main_node):
        super().__init__()
        self.main_window = main_window
        self.main_node   = main_node

        # self.tab_controller = TabController(
        #     self.main_window.main_node, self.main_window.tab_panel)
        # 监听tab切换信号
        # self.main_window.tab_panel.tabBar().tabBarClicked.connect(self.on_tab_clicked)
        self.main_window.tree_panel.nodeSelected.connect(self.main_window.property_panel.set_node)
        self.main_window.tree_panel.nodeSelected.connect(self.main_window.fig_panel.toolbar.set_node)
        # self.main_window.tree_panel.nodeSelected.connect(self.main_window.tab_panel.set_current_figure_tab_by_node)

        self.main_node["InputImage"].actionRequested.connect(self.main_window.on_action_requested)
        # cropRequested 信号现在由 InputImageNode 内部处理，触发工具栏按钮
    
    
