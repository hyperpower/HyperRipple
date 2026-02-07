import sys
import matplotlib

from .tree_node import *

class FigureNode(TreeNodeGroup):
    def __init__(self, name="Figure"):
        super().__init__(name)

        # add default children
        self.addChild(TreeNodeString("title", "My Figure"))
        self.addChild(TreeNodeNumber("width",  4))
        self.addChild(TreeNodeNumber("height", 3))
        self.addChild(TreeNodeNumber("dpi",  100))
        axes_node = TreeNodeGroup("Axes")
        axes_node.addChild(TreeNodeString("xlabel", "X-axis"))
        axes_node.addChild(TreeNodeString("ylabel", "Y-axis"))
        self.addChild(axes_node)


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
        



