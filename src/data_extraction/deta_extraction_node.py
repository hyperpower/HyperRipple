


from sys import path
from model.matplot_node import FigureNode
from model.tree_node import *
import view.predefined_matfig as predefined_matfig
from PySide6.QtCore import Signal, QObject

class AlignAxesNode(TreeNodeGroup):
    alignAxesRequested = Signal(object)  # 定义一个信号，用于请求对齐坐标轴

    def __init__(self, name="AlignAxes"):
        super().__init__(name)

        # add default properties
        x_axis = TreeNodeGroup("x_axis")
        x_axis.addChild(TreeNodeString("label", "X-axis"))
        x_axis.addChild(TreeNodeBoolean("is_log_scale", False))
        x_axis.add_allowed_action("Align X-axis in Figure", lambda: self.align_axes_in_figure_request("x_axis"))
        x0 = TreeNodeGroup("x0")
        x0.addChild(TreeNodeNumber("value", 0.0))
        x0.addChild(TreeNodeArray("point_pixel", []))
        x_axis.addChild(x0)
        x1 = TreeNodeGroup("x1")
        x1.addChild(TreeNodeNumber("value", 0.0))
        x1.addChild(TreeNodeArray("point_pixel", []))
        x_axis.addChild(x1)

        y_axis = TreeNodeGroup("y_axis")
        y_axis.addChild(TreeNodeString("label", "Y-axis"))
        y_axis.addChild(TreeNodeBoolean("is_log_scale", False))
        y_axis.add_allowed_action("Align Y-axis in Figure", lambda: self.align_axes_in_figure_request("y_axis"))
        y0 = TreeNodeGroup("y0")
        y0.addChild(TreeNodeNumber("value", 0.0))
        y0.addChild(TreeNodeArray("point_pixel", []))
        y_axis.addChild(y0)
        y1 = TreeNodeGroup("y1")
        y1.addChild(TreeNodeNumber("value", 0.0))
        y1.addChild(TreeNodeArray("point_pixel", []))
        y_axis.addChild(y1)

        self.addChild(x_axis)
        self.addChild(y_axis)

    def align_axes_in_figure_request(self, axis_name):
        if axis_name not in ["x_axis", "y_axis"]:
            raise ValueError(f"Invalid axis name: {axis_name}. Must be 'x_axis' or 'y_axis'.")
        node = self[axis_name]
        self.alignAxesRequested.emit(node)  # Emit signal to request aligning axes in the figure
    
    
    



class InputImageNode(TreeNodeGroup):
    loadRequested = Signal(object)  # 定义一个信号，用于请求打开图形界面

    def __init__(self, name="InputImage"):
        super().__init__(name)

        # add default properties
        path = TreeNodeString("path", "")
        self.addChild(path)
        image_width = TreeNodeNumber("image_width", "")
        # image_width.add_type("EDITABLE")
        self.addChild(image_width)
        
        image_height = TreeNodeNumber("image_height", "")
        self.addChild(image_height)

        # self._build_preview_figure("Preview")
        # matfig = predefined_matfig.blank_fig_with_dashed_grid()
        # fig_node = FigureNode("Preview")
        # self.addChild(fig_node)

    def allowed_actions(self):
        # 返回 (icon_name, action_name, handler)
        return [("load.svg", "Load Image ...", self.load_image)]

    def load_image(self):
        self.loadRequested.emit(self)  # Emit signal to request opening the figure
        


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