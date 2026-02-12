


from model.matplot_node import FigureNode
from model.tree_node import TreeNodeGroup, TreeNodeString
import view.predefined_matfig as predefined_matfig

class InputImageNode(TreeNodeGroup):
    def __init__(self, name="InputImage"):
        super().__init__(name)

        # add default properties
        path = TreeNodeString("path", "")
        self.addChild(path)

        # self._build_preview_figure("Preview")
        matfig = predefined_matfig.blank_fig_with_dashed_grid()
        fig_node = FigureNode("Preview", matfig)
        self.addChild(fig_node)

    
    # def _build_preview_figure(self, name="Preview"):
        
    #     # self.layoutChanged.emit(self, fig_node, "add")  
    #     return fig_node


class DataExtractionNode(TreeNodeGroup):
    def __init__(self, name="DataExtraction"):
        super().__init__(name)

        # add default children
        version_node = TreeNodeString("version", "1.0")
        version_node.set_editable(False)  # version is not editable
        self.addChild(version_node)

        self.addChild(InputImageNode("Input Image"))

        

        
class DataExtractionRootNode(TreeNodeGroup):
    def __init__(self, name="DE Root"):
        super().__init__(name)

        # add default children
        self.addChild(DataExtractionNode("DataExtraction"))