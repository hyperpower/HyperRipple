from PySide6.QtCore import QObject, Signal

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