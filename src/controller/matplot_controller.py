from PySide6.QtCore import QObject, Signal
from model.matplot_node import FigureNode
from view.aspect_ratio_container import AspectRatioContainer
from view.matplot_canvas import MatplotCanvas

class FigureController(QObject):
    def __init__(self, figure_node, canvas, parent=None):
        super().__init__(parent)

        self.figure_node = figure_node
        self.canvas = canvas

        self.connect_all_children()

    def on_data_changed(self, node, value):
        print(f"{node.parent.name} node {node.name} changed to value: {value}")
        
        
    def connect_recursive(self, node):
        node.dataChanged.connect(self.on_data_changed)
        for child in getattr(node, "children", []):
            self.connect_recursive(child)
    
    def connect_all_children(self):
        self.connect_recursive(self.figure_node)



class CanvasController(QObject):
    """Connects a Matplot model to a Matplot canvas."""
    figureAdded = Signal(object, str)  # Signal emitted when a new figure is added

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.matplot_node = main_window.main_node
        # List of open MatplotCanvas instances, 
        # (figure_node, canvas)
        self.open_canvases = [] 

        self.matplot_node.dataChanged.connect(self.on_data_changed)
        self.matplot_node.layoutChanged.connect(self.on_layout_changed)

        self.main_window.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)  

        self._init_connect()
    
    def _init_connect(self):
        for fn in self.matplot_node:
            if isinstance(fn, FigureNode):
                fn.openRequested.connect(self.on_figure_open_requested)
        

    def on_data_changed(self, node, value):
        """Redraw the canvas when the model changes."""
        # nbegin = self.matplot_node.getLeafChild(begin_index)  # 
        # print(f"Changed from: {nbegin}")
        print("Node name :", node.name, " changed to value:", value)
    
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
        canvas._render_figure_from_node(figure_node)  
        self.open_canvases.append((figure_node, canvas, controller))  # Store the controller as well
        figure_node.openRequested.connect(self.on_figure_open_requested)
        self.figureAdded.emit(canvas, figure_node.name)  # Emit signal
    
    def on_figure_open_requested(self, figure_node):
        """Handle the request to open a figure."""
        # Check if the figure is already open
        for fn, canvas, controller in self.open_canvases:
            if fn == figure_node:
                self.main_window.set_current_figure_tab(canvas)  # Bring to front
                return  # Already open

        # If not open, add a new figure
        self._add_figure(figure_node)

    def on_tab_close_requested(self, tab_index):
        """Handle the request to close a tab."""
        container = self.main_window.tab_widget.widget(tab_index)
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
                self.main_window.tab_widget.removeTab(tab_index)

class MainWindowController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.matplot_controller = CanvasController(
            self.main_window)
        
        self.matplot_controller.figureAdded.connect(self.main_window.add_new_figure_tab)
        

    
        