from PySide6.QtCore import QObject, Signal
from view.matplot_canvas import MatplotCanvas

class MatplotController(QObject):
    """Connects a Matplot model to a Matplot canvas."""
    figureAdded = Signal(object, str)  # Signal emitted when a new figure is added

    def __init__(self, matplot_node, canvas, parent=None):
        super().__init__(parent)
        self.matplot_node = matplot_node
        self.canvas = canvas

        self.matplot_node.dataChanged.connect(self.on_data_changed)
        self.matplot_node.layoutChanged.connect(self.on_layout_changed)

    def on_data_changed(self, begin_index, end_index, roles):
        """Redraw the canvas when the model changes."""
        # nbegin = self.matplot_node.getLeafChild(begin_index)  # 
        # print(f"Changed from: {nbegin}")
        self.canvas.draw_idle()
    
    def on_layout_changed(self, main_node, fig_node, msg):
        """Redraw the canvas when the layout changes."""
        print("Layout changed")
        if msg == "add":
            print(f"Figure added: {fig_node.name}")
            self.canvas.append(MatplotCanvas(
                width=fig_node["width"].value,
                height=fig_node["height"].value,
                dpi=fig_node["dpi"].value
            ))
            self.figureAdded.emit(self.canvas[-1], fig_node.name)  # Emit signal
        elif msg == "remove":
            print(f"Figure removed: {fig_node.name}")
        # self.canvas.draw_idle()

class MainWindowController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.matplot_controller = MatplotController(
            self.main_window.main_node,
            self.main_window.canvas)
        
        self.matplot_controller.figureAdded.connect(self.main_window.add_new_figure_tab)
        

    
        