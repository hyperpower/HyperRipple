from PySide6.QtCore import Qt
from matplotlib.patches import Rectangle


class CanvasZoomTool:
    """Canvas 缩放工具类，封装所有 zoom 相关的逻辑"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.main_ax = canvas.main_ax
        self._zooming = False
        self._zoom_start = None
        self._zoom_rect = None
        self._zoom_text = None
    
    def on_press(self, event):
        """处理鼠标按下事件 - 对应原 _handle_zoom_press"""
        # zoom 模式：记录起点
        self._zooming = True
        self._zoom_start = (event.xdata, event.ydata)
        # 创建虚线矩形
        self._zoom_rect = Rectangle(
            (event.xdata, event.ydata), 0, 0,
            linewidth=1, edgecolor='red', facecolor='none',
            linestyle='--'
        )
        self.main_ax.add_patch(self._zoom_rect)
        # 创建文字对象
        self._zoom_text = self.main_ax.text(
            event.xdata, event.ydata, "Zoom", color='red',
            ha='center', va='center', fontsize=8, zorder=10, visible=True
        )
        self.canvas.draw_idle()
    
    def on_motion(self, event):
        """处理鼠标移动事件 - 对应原 _handle_zoom_motion"""
        if self._zooming and self._zoom_start is not None:
            if event.xdata is None or event.ydata is None:
                return
            x0, y0 = self._zoom_start
            width = event.xdata - x0
            height = event.ydata - y0
            self._zoom_rect.set_width(width)
            self._zoom_rect.set_height(height)
            # 更新文字到框中心
            if width > 0:
                self._zoom_text.set_text("Zoom In")
            else:
                self._zoom_text.set_text("Zoom Out")
            if self._zoom_text is not None:
                cx = x0 + width / 2
                cy = y0 + height / 2
                self._zoom_text.set_position((cx, cy))
                self._zoom_text.set_visible(True)
            self.canvas.draw_idle()
    
    def on_release(self, event):
        """处理鼠标释放事件 - 对应原 _handle_zoom_release"""
        if not self._zooming:
            return

        self._zooming = False
        if self._zoom_rect is not None:
            self._zoom_rect.remove()
            self._zoom_rect = None
        if self._zoom_text is not None:
            self._zoom_text.remove()
            self._zoom_text = None
        if self._zoom_start is not None \
            and event.xdata is not None \
            and event.ydata is not None:
            x0, y0 = self._zoom_start
            x1, y1 = event.xdata, event.ydata
            if self._abs_fraction_on_axis(x0, x1, "x") < 0.05 \
                or self._abs_fraction_on_axis(y0, y1, "y") < 0.05:
                # 如果缩放区域太小，则认为是误操作，取消缩放
                self._zoom_start = None
                self.canvas.draw_idle()
                return
            # Zoom out 
            # Zoom in 
            if self.is_reverse_xaxis():
                x0, x1 = max(x0, x1), min(x0, x1)
            if self.is_reverse_yaxis():
                y0, y1 = max(y0, y1), min(y0, y1)
            self.main_ax.set_xlim(x0, x1)
            self.main_ax.set_ylim(y0, y1)
            self.canvas.draw_idle()
        self._zoom_start = None
    
    def _abs_fraction_on_axis(self, v0, v1, axis="x") -> float:
        """计算 v0 到 v1 在指定轴（x 或 y）上的绝对比例（0 到 1）。"""
        if axis == "x":
            ax_min, ax_max = self.main_ax.get_xlim()
        else:
            ax_min, ax_max = self.main_ax.get_ylim()
        if ax_max == ax_min:
            return 0.0
        return abs(v1 - v0) / abs(ax_max - ax_min)
    
    def is_reverse_yaxis(self) -> bool:
        """判断当前坐标轴是否为反向 Y 轴（图像坐标系）。"""
        ylim = self.main_ax.get_ylim()
        return ylim[0] > ylim[1]
    
    def is_reverse_xaxis(self) -> bool:
        """判断当前坐标轴是否为反向 X 轴。"""
        xlim = self.main_ax.get_xlim()
        return xlim[0] > xlim[1]