from PySide6.QtWidgets import QStyledItemDelegate, QSlider
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

class PropertyDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)


    def createEditor(self, parent, option, index):
        # child = model.leaf_children[index.row()] if hasattr(model, 'leaf_children') else None
        # # 只在第二列且类型为number时用滑块
        # if index.column() == 1 and getattr(child, 'type', None) == 'number':
        #     slider = QSlider(parent)
        #     slider.setOrientation(Qt.Horizontal)
        #     slider.setMinimum(0)
        #     slider.setMaximum(100)
        #     return slider
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        model = index.model()
        child = model.leaf_children[index.row()] if hasattr(model, 'leaf_children') else None
        if isinstance(editor, QSlider):
            editor.setValue(int(getattr(child, 'value', 0)))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        child = model.leaf_children[index.row()] if hasattr(model, 'leaf_children') else None
        if isinstance(editor, QSlider):
            model.setData(index, editor.value(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)