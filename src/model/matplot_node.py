import sys
import matplotlib

from .tree_node import *

class DataNode(TreeNodeBase):
    def __init__(self, name="Data", parent=None):
        super().__init__(name, parent)
        self.type = NTR.get("DATA") | NTR.get("OPENABLE")

        self.addChild(TreeNodeString("label", "Data Label"))
        self.addChild(TreeNodeArray("x", [1.0, 2.0, 3.0, 4.0, 5.0]))
        self.addChild(TreeNodeArray("y", [1.0, 2.8, 9.0, 16.0, 25.0]))

    def allowed_actions(self):
        return []

class AxesNode(TreeNodeGroup):
    def __init__(self, name="Axes", index=1):
        super().__init__(name)

        # add default children
        index_node = TreeNodeNumber("index", index)
        index_node.set_editable(False)
        self.addChild(index_node)
        
        self.addChild(TreeNodeString("xlabel", "X-axis"))
        self.addChild(TreeNodeString("ylabel", "Y-axis"))
        self.addChild(TreeNodeString("title", "My Axes"))
        self.addChild(TreeNodeNumber("xlim_min", 0))
        self.addChild(TreeNodeNumber("xlim_max", 1))
        self.addChild(TreeNodeNumber("ylim_min", 0))
        self.addChild(TreeNodeNumber("ylim_max", 1))

        self.addChild(DataNode("Data 1"))
    
    def default_properties(self):
        return {
            "index": 1,
            "xlabel": "X-axis",
            "ylabel": "Y-axis",
            "title": "My Axes",
            "xlim_min": 0,
            "xlim_max": 1,
            "ylim_min": 0,
            "ylim_max": 1
        }

class FigureNode(TreeNodeGroup):
    openRequested = Signal(object)  # 定义一个信号，用于请求打开图形界面

    def __init__(self, name="Figure"):
        super().__init__(name)

        # add default children
        # self.addChild(TreeNodeString("title", "My Figure"))
        # self.addChild(TreeNodeNumber("width",  4))
        # self.addChild(TreeNodeNumber("height", 3))
        # self.addChild(TreeNodeNumber("dpi",  100))
        # axes_grid_node = TreeNodeGroup("Axes Grid")
        # axes_grid_node.addChild(TreeNodeNumber("nrows", 1))
        # axes_grid_node.addChild(TreeNodeNumber("ncols", 1))
        # self.addChild(axes_grid_node)
        self.build_default_children(self.default_properties())

        axes_node = AxesNode("Axes")
        self.addChild(axes_node)
    
    def default_properties(self):
        return {
            "title": "My Figure",
            "width":  4,
            "height": 3,
            "axes_grid": {
                "nrows": 1,
                "ncols": 1
            }
        }
    
   
    def allowed_actions(self):
        return ["Open"]
    
    def open(self):
        self.openRequested.emit(self)  # Emit signal to request opening the figure


class MatplotNode(TreeNodeGroup):
    def __init__(self, name="Matplot"):
        super().__init__(name)

        # add default children
        version = matplotlib.__version__
        version_node = TreeNodeString("version", version)
        version_node.set_editable(False)  # version is not editable
        self.addChild(version_node)

        count_node = TreeNodeNumber("figure_count", self.count_figures())
        count_node.set_editable(False)  # figure count is not editable
        self.addChild(count_node)
    
    def count_figures(self):
        return len([child for child in self.children if isinstance(child, FigureNode)])

    def new_figure(self, name="Figure"):
        fig_node = FigureNode(name)
        self.addChild(fig_node)
        # Update figure count
        for child in self.children:
            if child.name == "figure_count":
                child.value = self.count_figures()
                break
        self.layoutChanged.emit(self, fig_node, "add")  
    
    def allowed_actions(self):
        return ["New Figure"]  # No actions allowed on MatplotNode
    
class MatplotRootNode(TreeNodeGroup):
    def __init__(self, name="Matplot Root"):
        super().__init__(name)

        # add default children
        self.addChild(MatplotNode("Matplot"))
        



