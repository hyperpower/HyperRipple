from PySide6.QtCore import Qt

class CanvasBrushTool:
    def __init__(self, canvas):
        self.canvas = canvas
        self._brushing = False
        self._brush_points = []
        self._brush_scatter = None
        self._brush_last_disp = None
        self._brush_size = 120  # points^2
        self._brush_spacing = 6  # pixels

    def on_press(self, event):
        if event.xdata is None or event.ydata is None:
            return
        self._brushing = True
        self._brush_points = []
        if self._brush_scatter is not None:
            try:
                self._brush_scatter.remove()
            except Exception:
                pass
            self._brush_scatter = None
        self._brush_scatter = self.canvas.main_ax.scatter(
            [], [], s=self._brush_size, c='#4caf50', alpha=0.25,
            edgecolors='none', zorder=5
        )
        self._brush_last_disp = (event.x, event.y)
        self.add_brush_point(event)
        self.canvas.draw_idle()

    def add_brush_point(self, event):
        if event.xdata is None or event.ydata is None:
            return
        self._brush_points.append((event.xdata, event.ydata))
        if self._brush_scatter is not None:
            self._brush_scatter.set_offsets(self._brush_points)

    def on_motion(self, event):
        if self._brushing:
            if event.xdata is None or event.ydata is None:
                return
            if self._brush_last_disp is None:
                self._brush_last_disp = (event.x, event.y)
                self.add_brush_point(event)
                self.canvas.draw_idle()
                return
            x0_disp, y0_disp = self._brush_last_disp
            dx = event.x - x0_disp
            dy = event.y - y0_disp
            if (dx * dx + dy * dy) >= (self._brush_spacing * self._brush_spacing):
                self._brush_last_disp = (event.x, event.y)
                self.add_brush_point(event)
                self.canvas.draw_idle()

    def on_release(self, event):
        if self._brushing:
            self._brushing = False
            self._brush_last_disp = None