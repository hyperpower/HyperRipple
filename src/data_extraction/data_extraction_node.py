from model.matplot_node import FigureNode
from model.tree_node import TreeNodeGroup, TreeNodeString
import view.predefined_matfig as predefined_matfig
from data_extraction.align_axes_node import AlignAxesNode
from data_extraction.input_image_node import InputImageNode


class DataExtractionNode(TreeNodeGroup):
    def __init__(self, name="DataExtraction"):
        super().__init__(name)

        self._main_fig = predefined_matfig.blank_fig_with_dashed_grid()

        # add default children
        version_node = TreeNodeString("version", "1.0")
        version_node.set_editable(False)  # version is not editable
        self.addChild(version_node)

        self.addChild(InputImageNode())
        self.addChild(AlignAxesNode())
    
    def allowed_actions(self):
        return []

        
class DataExtractionRootNode(TreeNodeGroup):
    def __init__(self, name="DE Root"):
        super().__init__(name)

        # add default children
        self.addChild(DataExtractionNode())