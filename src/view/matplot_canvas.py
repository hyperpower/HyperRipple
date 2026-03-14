from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseEvent
from view.canvas_tool.canvas_zoom_tool import CanvasZoomTool
from view.canvas_tool.canvas_crop_tool import CanvasCropTool
from view.canvas_tool.canvas_brush_tool import CanvasBrushTool
from view.canvas_tool.canvas_pan_tool import CanvasPanTool

class MatplotCanvas(FigureCanvas):
    def __init__(self, node, matfig=None, figsize=None):
        self._figure_node = node
        self._mode = None
        if matfig is not None:
            self.fig = matfig
            self.main_ax =  self.fig.axes[0]
        else:
            if figsize is not None:
                self.fig = Figure(figsize=figsize)
            else:
                self.fig = Figure()
            self.main_ax = self.fig.add_subplot(111)
        super(MatplotCanvas, self).__init__(self.fig)
        
        self.zoom_tool = CanvasZoomTool(self)
        self.crop_tool = CanvasCropTool(self)
        self.crop_tool.crop_completed.connect(self._on_crop_completed)
        self.brush_tool = CanvasBrushTool(self)
        self.pan_tool = CanvasPanTool(self)
        self._title_highlighted = False
        self._initial_xlim = None
        self._initial_ylim = None
        self._has_initial_view = False

        self._cid_press = self.mpl_connect('button_press_event', self._on_press)
        self._cid_motion = self.mpl_connect('motion_notify_event', self._on_motion)
        self._cid_release = self.mpl_connect('button_release_event', self._on_release)
        self._cid_scroll = self.mpl_connect('scroll_event', self._on_scroll)
        self._selected_line = None
        self._selected_line_prev_color = None
    
    def set_mode(self, mode: str | None):
        self._mode = mode
    
    def set_initial_view(self, xlim=None, ylim=None):
        if xlim is None:
            xlim = self.main_ax.get_xlim()
        if ylim is None:
            ylim = self.main_ax.get_ylim()
        if xlim[0] == 0.0 and xlim[1] == 1.0 and ylim[0] == 0.0 and ylim[1] == 1.0:
            self._initial_xlim = (0, 100)
            self._initial_ylim = (0, 100)
        else:
            self._initial_xlim = xlim
            self._initial_ylim = ylim
        self._has_initial_view = True
    
    def reset_view(self):
        if self._has_initial_view and self._initial_xlim is not None and self._initial_ylim is not None:
            self.main_ax.set_xlim(self._initial_xlim)
            self.main_ax.set_ylim(self._initial_ylim)
        else:
            self.main_ax.set_xlim(0, 100)
            self.main_ax.set_ylim(0, 100)
        self.draw_idle()
    
    def _render_figure_from_node(self, node):
        self.main_ax.clear()
        self.fig.suptitle(node["title"].value)
        for ax in node.iter_by_class("AxesNode"):
            self.main_ax.set_xlabel(ax["xlabel"].value)
            self.main_ax.set_ylabel(ax["ylabel"].value)
            self.main_ax.set_title(ax["title"].value)
            for data_node in ax.iter_by_class("DataNode"):
                x_data = data_node["x"].value
                y_data = data_node["y"].value
                self.main_ax.plot(x_data, y_data, label=data_node["label"].value)
        self._update_initial_view()
        self.main_ax.grid(True)
    
    def _update_initial_view(self):
        if not self._has_initial_view:
            xlim = self.main_ax.get_xlim()
            ylim = self.main_ax.get_ylim()
            self.set_initial_view(xlim, ylim)

    def highlight_title_if_clicked(self, event) -> bool:
        title_obj = self.main_ax.title
        if title_obj is None:
            return False
        try:
            hit, _ = title_obj.contains(event)
        except Exception:
            return False
        if not hit:
            return False
        on = not self._title_highlighted
        if on:
            title_obj.set_bbox(dict(boxstyle='round', fc='none', ec='#ff5722', lw=1.5, pad=0.3))
        else:
            title_obj.set_bbox(None)
        self._title_highlighted = on
        self.draw_idle()
        return True

    def highlight_line_if_clicked(self, event) -> bool:
        if event.inaxes is None or event.inaxes is not self.main_ax:
            return False
        for line in self.main_ax.get_lines():
            hit, _ = line.contains(event)
            if hit:
                if self._selected_line is not None and self._selected_line is not line:
                    try:
                        self._selected_line.set_color(self._selected_line_prev_color)
                    except Exception:
                        pass
                self._selected_line = line
                self._selected_line_prev_color = line.get_color()
                line.set_color('#ff9800')
                self.draw_idle()
                return True
        return False

    def _on_press(self, event):
        print(f"Mouse press at ({event.x}, {event.y}) in canvas coords, "
              f"data coords ({event.xdata}, {event.ydata}), "
              f"inaxes: {event.inaxes}")
        if event.button != 1 or event.inaxes is None or event.inaxes is not self.main_ax:
            return
        if self._mode == 'zoom':
            self.zoom_tool.on_press(event)
        elif self._mode == 'crop':
            self.crop_tool.on_press(event)
        elif self._mode == 'pan':
            self.pan_tool.on_press(event)
        elif self._mode == 'add_point':
            self._handle_add_point_press(event)
        elif self._mode == 'brush':
            self.brush_tool.on_press(event)
        else:
            self._handle_default_press(event)

    def _handle_add_point_press(self, event):
        if event.xdata is not None and event.ydata is not None:
            self.main_ax.plot(event.xdata, event.ydata, marker='o', color='red')
            self.draw_idle()
            print("after draw idel, added point at data coords ({}, {})".format(event.xdata, event.ydata))

    def _handle_default_press(self, event):
        if self.highlight_title_if_clicked(event):
            return
        if self.highlight_line_if_clicked(event):
            return

    def _on_motion(self, event):
        if self._mode == 'zoom':
            self.zoom_tool.on_motion(event)
        elif self._mode == 'crop':
            self.crop_tool.on_motion(event)
            return
        elif self._mode == 'pan':
            self.pan_tool.on_motion(event)
        elif self._mode == 'brush':
            self.brush_tool.on_motion(event)

    def _on_release(self, event):
        if event.button != 1:
            return
        if self._mode == 'zoom':
            self.zoom_tool.on_release(event)
        elif self._mode == 'crop':
            self.crop_tool.on_release(event)
            return
        elif self._mode == 'pan':
            self.pan_tool.on_release(event)
        elif self._mode == 'brush':
            self.brush_tool.on_release(event)
    
    def _on_scroll(self, event):
        if event.inaxes is None or event.inaxes is not self.main_ax:
            return
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return
        base_scale = 1.2
        scale = 1 / base_scale if event.button == 'up' else base_scale
        key = (event.key or '').lower()
        zoom_x = 'shift' not in key
        zoom_y = 'control' not in key and 'ctrl' not in key
        ax = self.main_ax
        if zoom_x:
            xmin, xmax = ax.get_xlim()
            ax.set_xlim(
                xdata - (xdata - xmin) * scale,
                xdata + (xmax - xdata) * scale
            )
        if zoom_y:
            ymin, ymax = ax.get_ylim()
            ax.set_ylim(
                ydata - (ydata - ymin) * scale,
                ydata + (ymax - ydata) * scale
            )
        self.draw_idle()

    def _on_crop_completed(self, x0, y0, x1, y1):
        print(f"Crop area selected: ({x0}, {y0}) to ({x1}, {y1})")