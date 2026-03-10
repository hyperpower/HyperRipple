from model.tree_node import *
from PySide6.QtCore import Signal


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