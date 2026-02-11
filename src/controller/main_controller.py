from PySide6.QtCore import QObject, Signal
from model.matplot_node import FigureNode
from view.aspect_ratio_container import AspectRatioContainer
from view.matplot_canvas import MatplotCanvas
from controller.tab_controller import TabController



class MainWindowController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.tab_controller = TabController(
            self.main_window.main_node, self.main_window.tab_panel)
        # 监听tab切换信号
        self.main_window.tab_panel.currentChanged.connect(self.on_tab_selection_changed)

    def on_tab_selection_changed(self, index):
        """
        link the tab panel with the tree panel selection
        """
        # tree_model = self.main_window.tree_panel.model
        # tree_model.print_all_rows()  # 调试输出树结构
        tab_widget = self.main_window.tab_panel.widget(index)
        if hasattr(tab_widget, '_canvas') and hasattr(tab_widget._canvas, '_figure_node'):
            figure_node = tab_widget._canvas._figure_node
            # 获取tree_model中figure_node对应的index
            tree_model = self.main_window.tree_panel.model
            tree_index = tree_model.index_from_node(figure_node)
            if tree_index.isValid():
                self.main_window.tree_panel.tree_view.setCurrentIndex(tree_index)
                self.main_window.tree_panel.nodeSelected.emit(figure_node)
        
       
        

    
        