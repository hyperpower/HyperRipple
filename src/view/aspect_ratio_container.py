from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QRect

class AspectRatioContainer(QWidget):
    """Place a single child widget scaled to fit while preserving an aspect ratio and centered."""
    def __init__(self, child: QWidget, aspect_ratio: float = 1.0, parent: QWidget | None = None):
        super().__init__(parent)
        self._child = child
        self._aspect = float(aspect_ratio) if aspect_ratio and aspect_ratio > 0 else 1.0
        self._child.setParent(self)
        self._child.show()

    def setAspectRatio(self, aspect_ratio: float):
        if aspect_ratio > 0:
            self._aspect = float(aspect_ratio)
            self._update_child_geometry()

    def resizeEvent(self, event):
        self._update_child_geometry()
        return super().resizeEvent(event)

    def _update_child_geometry(self):
        r = self.contentsRect()
        aw, ah = r.width(), r.height()
        if aw <= 0 or ah <= 0:
            return

        if aw / ah >= self._aspect:
            th = ah
            tw = int(round(th * self._aspect))
        else:
            tw = aw
            th = int(round(tw / self._aspect))

        x = r.x() + (aw - tw) // 2
        y = r.y() + (ah - th) // 2
        self._child.setGeometry(QRect(x, y, tw, th))