from model.tree_node import *
from PySide6.QtCore import Signal
import matplotlib.image as mpimg

class InputImageNode(TreeNodeGroup):
    actionRequested = Signal(object, str)  # 定义一个信号，用于请求操作，包含节点和操作名

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
        return [("load.svg", "Load Image ...", self.load_image),("crop.svg", "Crop Image", self.crop_image)]

    def load_image(self):
        self.actionRequested.emit(self, "load")  # Emit signal with action name for later steps
    
    def crop_image(self):
        # 触发工具栏的 crop 模式
        print("Crop image action triggered in InputImageNode")  # Debug log
        self.actionRequested.emit(self, "crop")  # Emit signal with action name for later steps
    
    def set_image(self, image):
        self._image = image

    def load_image_from_path(self, path):
        """
        使用路径加载图像文件，返回 numpy 数组（matplotlib.image）。
        """
        if not path:
            return None
        
        self._image = mpimg.imread(path)
        height, width = self._image.shape[:2]
        self["image_width"].set_value(width)
        self["image_height"].set_value(height)
        self["path"].set_value(path)
