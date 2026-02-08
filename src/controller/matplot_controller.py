from PySide6.QtCore import QObject, Signal
from view.matplot_canvas import MatplotCanvas

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

    def on_data_changed(self, begin_index, end_index, roles):
        """Redraw the canvas when the model changes."""
        # nbegin = self.matplot_node.getLeafChild(begin_index)  # 
        # print(f"Changed from: {nbegin}")
        self.open_canvases.draw_idle()
    
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
        canvas = MatplotCanvas(
            width=figure_node["width"].value,
            height=figure_node["height"].value,
            dpi=figure_node["dpi"].value
        )
        canvas._figure_node = figure_node  # Store reference for closing
        self.open_canvases.append((figure_node, canvas))
        figure_node.openRequested.connect(self.on_figure_open_requested)
        self.figureAdded.emit(canvas, figure_node.name)  # Emit signal
    
    def on_figure_open_requested(self, figure_node):
        """Handle the request to open a figure."""
        # Check if the figure is already open
        for fn, canvas in self.open_canvases:
            if fn == figure_node:
                self.main_window.tab_widget.setCurrentWidget(canvas)
                print(f"Figure {figure_node.name} is already open.")
                return  # Already open

        # If not open, add a new figure
        self._add_figure(figure_node)

    def on_tab_close_requested(self, tab_index):
        """Handle the request to close a tab."""
        canvas = self.main_window.tab_widget.widget(tab_index)
        
        if canvas is None or not hasattr(canvas, '_figure_node'):
            return
        
        figure_node = canvas._figure_node
        self.open_canvases = [(fn, c) for fn, c in self.open_canvases if c != canvas]
        self.main_window.tab_widget.removeTab(tab_index)
        print(f"Figure {figure_node.name} closed.")

class MainWindowController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.matplot_controller = CanvasController(
            self.main_window)
        
        self.matplot_controller.figureAdded.connect(self.main_window.add_new_figure_tab)
        

    
        