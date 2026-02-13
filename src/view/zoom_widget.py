from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt

from view.matplot_canvas import MatplotCanvas
from view.view_helper import createThemedIcon

class ZoomWidget(QWidget):
    def __init__(self, source_canvas, parent=None):
        super().__init__(parent)
        self.source_canvas = source_canvas
        self.zoom_canvas = MatplotCanvas(None)
        # self.zoom_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._data_bounds = None
        self._default_zoom_window = (150, 150)
        self._zoom_window = self._default_zoom_window
        self._last_zoom_center = None
        self._zoom_crosshair_v = None
        self._zoom_crosshair_h = None

        self.source_canvas.mpl_connect('motion_notify_event', self._on_source_motion)
        self.source_canvas.mpl_connect('scroll_event', self._on_source_scroll)
        self.source_canvas.mpl_connect('draw_event', self._on_source_draw)

        layout = QVBoxLayout(self)

        self._zoom_toggle_btn = QToolButton(self)
        self._zoom_toggle_btn.setText("放大镜")
        self._zoom_toggle_btn.setArrowType(Qt.NoArrow)
        _icon = createThemedIcon("asset/icons/down_circle.svg")
        self._zoom_toggle_btn.setIcon(_icon)
        self._zoom_toggle_btn.setIconSize(QSize(18, 18))
        self._zoom_toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._zoom_toggle_btn.setAutoRaise(True)
        self._zoom_toggle_btn.setFixedHeight(24)
        self._zoom_toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._zoom_toggle_btn.clicked.connect(self._toggle_zoom_widget)
        layout.addWidget(self._zoom_toggle_btn)

        self._content = QWidget(self)
        content_layout = QVBoxLayout(self._content)
        content_layout.addWidget(self.zoom_canvas)

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
        self._content.setLayout(content_layout)

        layout.addWidget(self._content)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setMinimumSize(220, 220)

    def sizeHint(self):
        return QSize(200, 200)

    def _toggle_zoom_widget(self):
        collapsed = self._content.isVisible()
        self._content.setVisible(not collapsed)
        if collapsed:
            _icon = createThemedIcon("asset/icons/right_circle.svg")
        else:
            _icon = createThemedIcon("asset/icons/down_circle.svg")
        self._zoom_toggle_btn.setIcon(_icon)

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
        if self._data_bounds is None or self.zoom_canvas.axes is None:
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
        cx = max(xmin + half_w, min(xmax - half_w, cx))
        cy = max(ymin + half_h, min(ymax - half_h, cy))
        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.axes.get_xlim()
        ylim = self.source_canvas.axes.get_ylim()
        self.zoom_canvas.axes.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.axes.set_xlim(x1, x0)
        self.zoom_canvas.axes.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.axes.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()

    def _on_source_draw(self, event):
        if event.canvas is not self.source_canvas:
            return
        self._sync_zoom_from_source_axes()

    def _sync_zoom_from_source_axes(self):
        prev_xlim = None
        prev_ylim = None
        if self.zoom_canvas.axes is not None:
            prev_xlim = self.zoom_canvas.axes.get_xlim()
            prev_ylim = self.zoom_canvas.axes.get_ylim()

        src_ax = self.source_canvas.axes
        if src_ax is None:
            return

        zoom_fig = self.zoom_canvas.figure
        if self.zoom_canvas.axes is None:
            self.zoom_canvas.axes = zoom_fig.add_subplot(111)

        ax = self.zoom_canvas.axes
        ax.clear()
        ax.set_facecolor(src_ax.get_facecolor())

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

        ax.set_aspect(src_ax.get_aspect())
        ax.set_axis_off()

        self._zoom_crosshair_v = ax.axvline(
            0, color="#ff5722", linewidth=1.0, linestyle='--', zorder=10
        )
        self._zoom_crosshair_h = ax.axhline(
            0, color="#ff5722", linewidth=1.0, linestyle='--', zorder=10
        )

        xlim = src_ax.get_xlim()
        ylim = src_ax.get_ylim()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        xmin, xmax = sorted(xlim)
        ymin, ymax = sorted(ylim)
        self._data_bounds = (xmin, xmax, ymin, ymax)

        if prev_xlim is not None and prev_ylim is not None:
            ax.set_xlim(prev_xlim)
            ax.set_ylim(prev_ylim)
            self._last_zoom_center = (
                (prev_xlim[0] + prev_xlim[1]) / 2,
                (prev_ylim[0] + prev_ylim[1]) / 2,
            )
            cx, cy = self._last_zoom_center
            if self._zoom_crosshair_v is not None:
                self._zoom_crosshair_v.set_xdata([cx, cx])
            if self._zoom_crosshair_h is not None:
                self._zoom_crosshair_h.set_ydata([cy, cy])

        zoom_fig.tight_layout(pad=0)
        self.zoom_canvas.draw_idle()

    def _on_source_motion(self, event):
        if event.inaxes is None or event.inaxes is not self.source_canvas.axes:
            return
        if event.xdata is None or event.ydata is None:
            return
        if self._data_bounds is None or self.zoom_canvas.axes is None:
            return

        xmin, xmax, ymin, ymax = self._data_bounds
        win_w, win_h = self._zoom_window
        half_w = win_w / 2
        half_h = win_h / 2

        cx = max(xmin + half_w, min(xmax - half_w, event.xdata))
        cy = max(ymin + half_h, min(ymax - half_h, event.ydata))

        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.axes.get_xlim()
        ylim = self.source_canvas.axes.get_ylim()
        self.zoom_canvas.axes.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.axes.set_xlim(x1, x0)
        self.zoom_canvas.axes.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.axes.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()

    def _on_source_scroll(self, event):
        if event.inaxes is None or event.inaxes is not self.source_canvas.axes:
            return
        if self._data_bounds is None or self.zoom_canvas.axes is None:
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
        cx = max(xmin + half_w, min(xmax - half_w, cx))
        cy = max(ymin + half_h, min(ymax - half_h, cy))
        self._last_zoom_center = (cx, cy)

        if self._zoom_crosshair_v is not None:
            self._zoom_crosshair_v.set_xdata([cx, cx])
        if self._zoom_crosshair_h is not None:
            self._zoom_crosshair_h.set_ydata([cy, cy])

        x0, x1 = cx - half_w, cx + half_w
        y0, y1 = cy - half_h, cy + half_h
        xlim = self.source_canvas.axes.get_xlim()
        ylim = self.source_canvas.axes.get_ylim()
        self.zoom_canvas.axes.set_xlim(x0, x1) if xlim[0] < xlim[1] else self.zoom_canvas.axes.set_xlim(x1, x0)
        self.zoom_canvas.axes.set_ylim(y0, y1) if ylim[0] < ylim[1] else self.zoom_canvas.axes.set_ylim(y1, y0)
        self.zoom_canvas.draw_idle()
