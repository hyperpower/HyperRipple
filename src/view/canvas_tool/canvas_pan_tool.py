from PySide6.QtCore import Qt

class CanvasPanTool:
    def __init__(self, canvas):
        self.canvas = canvas
        self._panning = False
        self._press_disp = None
        self._press_xlim = None
        self._press_ylim = None
        self._inv_trans = None

    def on_press(self, event):
        self.canvas.setCursor(Qt.ClosedHandCursor)
        self._panning = True
        self._press_disp = (event.x, event.y)
        self._press_xlim = self.canvas.main_ax.get_xlim()
        self._press_ylim = self.canvas.main_ax.get_ylim()
        self._inv_trans = self.canvas.main_ax.transData.inverted()

    def on_motion(self, event):
        if self._panning and self._press_disp is not None:
            if self.canvas.cursor().shape() != Qt.ClosedHandCursor:
                self.canvas.setCursor(Qt.SizeAllCursor)
            x0_disp, y0_disp = self._press_disp
            x1_disp, y1_disp = event.x, event.y
            x0_data, y0_data = self._inv_trans.transform((x0_disp, y0_disp))
            x1_data, y1_data = self._inv_trans.transform((x1_disp, y1_disp))
            dx = x1_data - x0_data
            dy = y1_data - y0_data
            xl0, xl1 = self._press_xlim
            yl0, yl1 = self._press_ylim
            self.canvas.main_ax.set_xlim(xl0 - dx, xl1 - dx)
            self.canvas.main_ax.set_ylim(yl0 - dy, yl1 - dy)
            self.canvas.draw_idle()

    def on_release(self, event):
        if self._panning:
            if self.canvas._mode == 'pan':
                self.canvas.setCursor(Qt.OpenHandCursor)
            else:
                self.canvas.unsetCursor()
            self._panning = False
            self._press_disp = None
            self._press_xlim = None
            self._press_ylim = None