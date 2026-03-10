from model.tree_node import *
from PySide6.QtCore import Signal


class InputImageNode(TreeNodeGroup):
    loadRequested = Signal(object)  # 定义一个信号，用于请求打开图形界面

    def __init__(self, name="InputImage"):
        super().__init__(name)
        self._image = None

        # add default properties
        path = TreeNodeString("path", "")
        self.addChild(path)
        image_width = TreeNodeNumber("image_width", "")
        # image_width.add_type("EDITABLE")
        self.addChild(image_width)
        
        image_height = TreeNodeNumber("image_height", "")
        self.addChild(image_height)

    def allowed_actions(self):
        # 返回 (icon_name, action_name, handler)
        return [("load.svg", "Load Image ...", self.load_image)]

    def load_image(self):
        self.loadRequested.emit(self)  # Emit signal to request opening the figure
    
    def set_image(self, image):
        self._image = image
