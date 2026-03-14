from .input_image_node import InputImageNode

class ProcessedImageNode(InputImageNode):
    """
    用于存储经过如 crop 等操作处理后的图像结果的节点。
    """
    def __init__(self, processe_type = None, processed_image=None ):
        self._processed_image = processed_image
        self._processe_type = processe_type
    
    
    def set_processed_image(self, image):
        self._processed_image = image