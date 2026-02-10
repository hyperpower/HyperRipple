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
        
       
        

    
        