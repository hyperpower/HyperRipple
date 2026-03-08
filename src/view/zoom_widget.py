from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import QSize

from view.matplot_canvas import MatplotCanvas
from view.dropdown_widget import DropDownWidget


class ZoomWidget(DropDownWidget):
    def __init__(self, source_canvas, parent=None):
        super().__init__("放大镜", parent)
        self.source_canvas = source_canvas
        self.zoom_canvas = None
        self._data_bounds = None
        self._default_zoom_window = (150, 150)
        self._zoom_window = self._default_zoom_window
        self._last_zoom_center = None

        self._zoom_crosshair_v = None
        self._zoom_crosshair_h = None

        self.source_canvas.mpl_connect('motion_notify_event', self._on_source_motion)
        self.source_canvas.mpl_connect('scroll_event', self._on_source_scroll)
        self.source_canvas.mpl_connect('draw_event', self._on_source_draw)

        self.setContentBuilder(self._build_content_widget)
        self.setMinimumWidth(220)

    def _build_content_widget(self):
        print("Building Zoom Content Widget")
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        self.zoom_canvas = MatplotCanvas(None, figsize=(2, 2))
        # 设置 QSizePolicy 为 Expanding，让 zoom_canvas 占据更多空间
        self.zoom_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.zoom_canvas.setMinimumSize(200, 200)
        content_layout.addWidget(self.zoom_canvas, stretch=1)

        controls = QHBoxLayout()
        reset_btn = QPushButton("恢复", self)
        zoom_in_btn = QPushButton("放大", self)
        zoom_out_btn = QPushButton("缩小", self)
        reset_btn.clicked.connect(self._on_zoom_reset)
        zoom_in_btn.clicked.connect(lambda: self._apply_zoom_factor(0.9))
        zoom_out_btn.clicked.connect(lambda: self._apply_zoom_factor(1.1))
        controls.addWidget(reset_btn)
        controls.addWidget(zoom_in_btn)
        controls.addWidget(zoom_out_btn)
        content_layout.addLayout(controls)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        if self.source_canvas is not None and self.source_canvas.main_ax is not None:
            self._sync_zoom_from_source_axes()
        return content_widget

    def sizeHint(self):
        if self.isCollapsed():
            return QSize(200, 24)
        return QSize(200, 200)

    def _on_zoom_reset(self):
        self._zoom_window = self._default_zoom_window
        self._apply_zoom_to_center()

    def _apply_zoom_factor(self, factor):
        if self._data_bounds is None:
            return
        xmin, xmax, ymin, ymax = self._data_bounds
        x_range = max(xmax - xmin, 1e-6)
        y_range = max(ymax - ymin, 1e-6)

        win_w, win_h = self._zoom_window
        min_w = max(1e-6, x_range * 0.02)
        min_h = max(1e-6, y_range * 0.02)
        new_w = max(min_w, min(x_range, win_w * factor))
        new_h = max(min_h, min(y_range, win_h * factor))
        self._zoom_window = (new_w, new_h)
        self._apply_zoom_to_center()

    def _apply_zoom_to_center(self):
        if self._data_bounds is None or self.zoom_canvas is None or self.zoom_canvas.main_ax is None:
            return

        xmin, xmax, ymin, ymax = self._data_bounds
        if self._last_zoom_center is None:
            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
        else:
            cx, cy = self._last_zoom_center

        win_w, win_h = self._zoom_window
        half_w = win_w / 2
        half_h = win_h / 2
        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.main_ax.get_xlim()
        ylim = self.source_canvas.main_ax.get_ylim()
        self.zoom_canvas.main_ax.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.main_ax.set_xlim(x1, x0)
        self.zoom_canvas.main_ax.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.main_ax.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()

    def _on_source_draw(self, event):
        if event.canvas is not self.source_canvas:
            return
        self._sync_zoom_from_source_axes()

    def _sync_zoom_from_source_axes(self):
        """同步主图坐标轴到缩放窗口。"""
        if self.zoom_canvas is None:
            return
        
        src_ax = self.source_canvas.main_ax
        if src_ax is None:
            return

        # 确保 zoom_canvas 有 axes
        if self.zoom_canvas.main_ax is None:
            self.zoom_canvas.main_ax = self.zoom_canvas.figure.add_subplot(111)

        ax = self.zoom_canvas.main_ax
        
        # 1. 清空并复制背景色
        ax.clear()
        ax.set_facecolor(src_ax.get_facecolor())
        
        # 2. 复制坐标轴内容（images, lines, collections）
        self._copy_axis_content(src_ax, ax)
        
        # 3. 复制 grid 样式
        self._copy_grid_style(src_ax, ax)
        
        # 4. 添加十字线
        self._add_crosshair(ax)
        
        # 5. 保存数据边界
        xlim = src_ax.get_xlim()
        ylim = src_ax.get_ylim()
        xmin, xmax = sorted(xlim)
        ymin, ymax = sorted(ylim)
        self._data_bounds = (xmin, xmax, ymin, ymax)
        
        # 6. 设置默认的 zoom 窗口为主图坐标范围的 1/3
        x_range = abs(xmax - xmin)
        y_range = abs(ymax - ymin)
        self._default_zoom_window = (x_range / 3, y_range / 3)
        
        # 7. 初始化或更新 zoom 窗口
        # 使用 self._last_zoom_center 判断是否是首次初始化
        self._init_or_update_zoom_window(ax, xmin, xmax, ymin, ymax)
        self.zoom_canvas.figure.tight_layout(pad=0.2)

        
        self.zoom_canvas.draw_idle()

    def _copy_axis_content(self, src_ax, ax):
        """复制坐标轴内容：images, lines, collections。"""
        # 复制 images
        for img in src_ax.images:
            vmin, vmax = img.get_clim()
            ax.imshow(
                img.get_array(),
                extent=img.get_extent(),
                origin=img.origin,
                cmap=img.get_cmap(),
                interpolation=img.get_interpolation(),
                vmin=vmin,
                vmax=vmax,
            )

        # 复制 lines
        for line in src_ax.get_lines():
            ax.plot(
                line.get_xdata(),
                line.get_ydata(),
                color=line.get_color(),
                linestyle=line.get_linestyle(),
                linewidth=line.get_linewidth(),
                marker=line.get_marker(),
                markersize=line.get_markersize(),
                alpha=line.get_alpha(),
            )

        # 复制 collections (scatter 等)
        for col in src_ax.collections:
            offsets = col.get_offsets()
            if offsets is None or len(offsets) == 0:
                continue
            ax.scatter(
                offsets[:, 0],
                offsets[:, 1],
                s=col.get_sizes(),
                c=col.get_facecolor(),
                edgecolors=col.get_edgecolor(),
                linewidths=col.get_linewidths(),
                alpha=col.get_alpha(),
            )

    def _copy_grid_style(self, src_ax, ax):
        """复制 grid 状态和样式。"""
        x_gridlines = src_ax.xaxis.get_gridlines()
        y_gridlines = src_ax.yaxis.get_gridlines()
        x_grid_on = len(x_gridlines) > 0 and x_gridlines[0].get_visible()
        y_grid_on = len(y_gridlines) > 0 and y_gridlines[0].get_visible()
        
        xlim = src_ax.get_xlim()
        ylim = src_ax.get_ylim()

        if x_grid_on or y_grid_on:
            if x_gridlines:
                grid_line = x_gridlines[0]
                grid_color = grid_line.get_color()
                grid_linestyle = grid_line.get_linestyle()
                grid_linewidth = grid_line.get_linewidth()
                grid_alpha = grid_line.get_alpha()
                
                # 复制主图的 minor tick 状态
                x_minorticks = src_ax.get_xticks(minor=True)
                y_minorticks = src_ax.get_yticks(minor=True)
                
                # 设置 major ticks 和 minor ticks
                ax.set_xticks(src_ax.get_xticks())
                ax.set_yticks(src_ax.get_yticks())
                ax.set_xticks(x_minorticks, minor=True)
                ax.set_yticks(y_minorticks, minor=True)
                
                ax.grid(True, which='both', color=grid_color, linestyle=grid_linestyle, 
                        linewidth=grid_linewidth, alpha=grid_alpha)
        
        # 在设置 ticks 之后再设置 xlim/ylim，防止被覆盖
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_aspect(src_ax.get_aspect())

    def _add_crosshair(self, ax):
        """添加十字线。"""
        try:
            self._zoom_crosshair_v = ax.axvline(
                0, color="#ff5722", linewidth=1.0, linestyle='--', zorder=10
            )
            self._zoom_crosshair_h = ax.axhline(
                0, color="#ff5722", linewidth=1.0, linestyle='--', zorder=10
            )
        except Exception:
            self._zoom_crosshair_v = None
            self._zoom_crosshair_h = None

    def _init_or_update_zoom_window(self, ax, xmin, xmax, ymin, ymax):
        """初始化或更新 zoom 窗口。"""
        # 如果是首次初始化，设置居中显示
        if self._last_zoom_center is None:
            center_x = (xmin + xmax) / 2
            center_y = (ymin + ymax) / 2
            self._last_zoom_center = (center_x, center_y)
            self._zoom_window = self._default_zoom_window
            # 应用初始 zoom 设置
            half_w = self._default_zoom_window[0] / 2
            half_h = self._default_zoom_window[1] / 2
            ax.set_xlim(center_x - half_w, center_x + half_w)
            ax.set_ylim(center_y - half_h, center_y + half_h)
        else:
            # 保持之前的 zoom 窗口
            cx, cy = self._last_zoom_center
            half_w, half_h = self._zoom_window[0] / 2, self._zoom_window[1] / 2
            ax.set_xlim(cx - half_w, cx + half_w)
            ax.set_ylim(cy - half_h, cy + half_h)
            if self._zoom_crosshair_v is not None:
                self._zoom_crosshair_v.set_xdata([cx, cx])
            if self._zoom_crosshair_h is not None:
                self._zoom_crosshair_h.set_ydata([cy, cy])

    def _on_source_motion(self, event):
        if event.inaxes is None or event.inaxes is not self.source_canvas.main_ax:
            return
        if event.xdata is None or event.ydata is None:
            return
        if self._data_bounds is None or self.zoom_canvas is None or self.zoom_canvas.main_ax is None:
            return

        xmin, xmax, ymin, ymax = self._data_bounds
        win_w, win_h = self._zoom_window
        half_w = win_w / 2
        half_h = win_h / 2

        cx = event.xdata
        cy = event.ydata

        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.main_ax.get_xlim()
        ylim = self.source_canvas.main_ax.get_ylim()
        self.zoom_canvas.main_ax.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.main_ax.set_xlim(x1, x0)
        self.zoom_canvas.main_ax.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.main_ax.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()

    def _on_source_scroll(self, event):
        if event.inaxes is None or event.inaxes is not self.source_canvas.main_ax:
            return
        if self._data_bounds is None or self.zoom_canvas is None or self.zoom_canvas.main_ax is None:
            return

        xmin, xmax, ymin, ymax = self._data_bounds
        x_range = max(xmax - xmin, 1e-6)
        y_range = max(ymax - ymin, 1e-6)
        win_w, win_h = self._zoom_window
        scale = 1 / 1.2 if event.button == 'up' else 1.2

        min_w = max(1e-6, x_range * 0.02)
        min_h = max(1e-6, y_range * 0.02)
        new_w = max(min_w, min(x_range, win_w * scale))
        new_h = max(min_h, min(y_range, win_h * scale))
        self._zoom_window = (new_w, new_h)

        if self._last_zoom_center is None:
            if event.xdata is None or event.ydata is None:
                return
            cx, cy = event.xdata, event.ydata
        else:
            cx, cy = self._last_zoom_center
        half_w = new_w / 2
        half_h = new_h / 2
        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.main_ax.get_xlim()
        ylim = self.source_canvas.main_ax.get_ylim()
        self.zoom_canvas.main_ax.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.main_ax.set_xlim(x1, x0)
        self.zoom_canvas.main_ax.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.main_ax.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()
