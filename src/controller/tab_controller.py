import sys
from PySide6.QtCore import QObject, Signal
from model.matplot_node import MatplotNode, FigureNode
from view.aspect_ratio_container import AspectRatioContainer
from view.matplot_canvas import MatplotCanvas
from controller.figure_controller import FigureController


class TabController(QObject):

    """Connects a Matplot model to a Matplot canvas."""
    figureAdded = Signal(object, str)  # Signal emitted when a new figure is added

    def __init__(self, main_node, tab_panel, parent=None):
        super().__init__(parent)
        self.tab_panel = tab_panel
        self.main_node = main_node
        # List of open MatplotCanvas instances, 
        # (figure_node, canvas)
        self.open_canvases = [] 

        self.main_node.dataChanged.connect(self.on_data_changed)
        self.main_node.layoutChanged.connect(self.on_layout_changed)

        self.tab_panel.tabCloseRequested.connect(self.on_tab_close_requested)  
        self.figureAdded.connect(self.tab_panel.add_new_figure_tab)

        self._init_connect()

    def recursive_connect(self, node):
        for child in node:
            if isinstance(child, FigureNode):
                child.openRequested.connect(self.on_figure_open_requested)
            # 递归遍历子节点
            self.recursive_connect(child)

    def _init_connect(self):
        self.recursive_connect(self.main_node)
    
    def get_canvas_by_figure_node(self, figure_node):
        """Retrieve the canvas associated with a given figure node."""
        for fn, canvas, controller in self.open_canvases:
            if fn == figure_node:
                return canvas
        return None
        

    def on_data_changed(self, node, value):
        """Redraw the canvas when the model changes."""
        # nbegin = self.matplot_node.getLeafChild(begin_index)  # 
        # print(f"Changed from: {nbegin}")
        if node.name in ["width", "height"]:
            canvas = self.get_canvas_by_figure_node(node.parent)
            if canvas:
                fn = node.parent
                aspect_ratio = fn["width"].value / fn["height"].value
                self.tab_panel.update_figure_aspect_ratio(canvas, aspect_ratio)
    
    def on_layout_changed(self, main_node, fig_node, msg):
        """Redraw the canvas when the layout changes."""
        print("Layout changed")
        if msg == "add":
            self._add_figure(fig_node)  
        elif msg == "remove":
            print(f"Figure removed: {fig_node.name}")
        # self.canvas.draw_idle()
    
    def _add_figure(self, figure_node):
        """Add a new figure canvas for the given figure node."""
        canvas = MatplotCanvas(figure_node)
        controller = FigureController(figure_node, canvas)
        figure_node["width"].dataChanged.connect(self.on_data_changed)
        figure_node["height"].dataChanged.connect(self.on_data_changed)
        canvas._render_figure_from_node(figure_node)  
        self.open_canvases.append((figure_node, canvas, controller))  # Store the controller as well
        figure_node.openRequested.connect(self.on_figure_open_requested)
        self.figureAdded.emit(canvas, figure_node.name)  # Emit signal
    
    def on_figure_open_requested(self, figure_node):
        """Handle the request to open a figure."""
        # Check if the figure is already open
        for fn, canvas, controller in self.open_canvases:
            if fn == figure_node:
                self.tab_panel.set_current_figure_tab(canvas)  # Bring to front
                return  # Already open

        # If not open, add a new figure
        self._add_figure(figure_node)

    def on_tab_close_requested(self, tab_index):
        """Handle the request to close a tab."""
        container = self.tab_panel.widget(tab_index)
        if isinstance(container, AspectRatioContainer) and hasattr(container, '_canvas'):
            canvas = container._canvas
            if canvas is None or not hasattr(canvas, '_figure_node'):
                return
            else:
                # remove canvas from open_canvases
                for i, (fn, c, con) in enumerate(self.open_canvases):
                    if c == canvas:
                        self.open_canvases.pop(i)
                        break
                self.tab_panel.removeTab(tab_index)
