import sys

import matplotlib

from .tree_node import *

class FigureNode(TreeNodeGroup):
    def __init__(self, name="Figure"):
        super().__init__(name)

        # add default children
        self.addChild(TreeNodeString("title", "My Figure"))
        self.addChild(TreeNodeNumber("width", 800))
        self.addChild(TreeNodeNumber("height", 600))
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
        # self.addChild(TreeNodeNumber("test number", 1))
    
class MatplotRootNode(TreeNodeGroup):
    def __init__(self, name="Matplot Root"):
        super().__init__(name)

        # add default children
        self.addChild(MatplotNode("Matplot"))
        



