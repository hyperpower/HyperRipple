from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseEvent
from matplotlib.patches import Rectangle


class MatplotCanvas(FigureCanvas):
    def __init__(self, node, matfig = None):
        self._figure_node = node
        self._mode = None
        if matfig is not None:
            self.fig = matfig
        else:
            self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        # self.axes.set_aspect("equal")
        # self.fig.subplots_adjust(left=0.1, right=0.9, bottom=0.12, top=0.92)
        super(MatplotCanvas, self).__init__(self.fig)
        
        
        # zoom 
        self._zooming = False
        self._zoom_start = None
        self._zoom_rect = None  # 用于显示缩放区域的矩形补丁
        # pan
        self._panning = False
        self._press_disp = None      # 按下时的显示坐标 (event.x, event.y)
        self._press_xlim = None
        self._press_ylim = None
        self._inv_trans = self.axes.transData.inverted()

        # 标题高亮状态
        self._title_highlighted = False

        # 连接事件
        self._cid_press   = self.mpl_connect('button_press_event', self._on_press)
        self._cid_motion  = self.mpl_connect('motion_notify_event', self._on_motion)
        self._cid_release = self.mpl_connect('button_release_event', self._on_release)
        # 鼠标滚轮缩放数据区域
        self._cid_scroll = self.mpl_connect('scroll_event', self._on_scroll)
        # 选中线的状态
        self._selected_line = None
        self._selected_line_prev_color = None
    
    def set_mode(self, mode: str | None):
        """设置当前交互模式：'pan' 或 None。"""
        self._mode = mode
    
    def _render_figure_from_node(self, node):
        """根据 FigureNode 的属性渲染图形内容。"""
        self.axes.clear()
        # self.fig.set_figwidth(node["width"].value)
        # self.fig.set_figheight(node["height"].value)
        # self.fig.set_dpi(50)
        self.fig.suptitle(node["title"].value)

        for ax in node.iter_by_class("AxesNode"):
            self.axes.set_xlabel(ax["xlabel"].value)
            self.axes.set_ylabel(ax["ylabel"].value)
            self.axes.set_title(ax["title"].value)
            for data_node in ax.iter_by_class("DataNode"):
                x_data = data_node["x"].value
                y_data = data_node["y"].value
                self.axes.plot(x_data, y_data, label=data_node["label"].value)

        # self.axes.set_xlim(node["Axes"]["xlim_min"].value, node["Axes"]["xlim_max"].value)
        # self.axes.set_ylim(node["Axes"]["ylim_min"].value, node["Axes"]["ylim_max"].value)
        # Get data from DataNode children
        self.axes.grid(True)


    def highlight_title_if_clicked(self, event) -> bool:
        """
        判断是否点击了标题；若点击，则显示/切换标题边框并返回 True，否则返回 False。
        """
        title_obj = self.axes.title  # Text 对象
        if title_obj is None:
            return False
        try:
            hit, _ = title_obj.contains(event)  # 使用 mpl 事件坐标判定命中
        except Exception:
            return False
        if not hit:
            return False

        # 切换高亮（也可改为始终显示：on=True）
        on = not self._title_highlighted
        if on:
            title_obj.set_bbox(dict(boxstyle='round', fc='none', ec='#ff5722', lw=1.5, pad=0.3))
        else:
            title_obj.set_bbox(None)
        self._title_highlighted = on
        self.draw_idle()
        return True

    def highlight_line_if_clicked(self, event) -> bool:
        """
        若在数据区域点击到了某条线，则将其颜色改为橙色并返回 True；否则返回 False。
        会自动还原上一次被高亮的线的原始颜色。
        """
        if event.inaxes is None or event.inaxes is not self.axes:
            return False
        for line in self.axes.get_lines():
            hit, _ = line.contains(event)  # 使用 mpl 事件进行命中测试
            if hit:
                # 还原之前高亮线的颜色
                if self._selected_line is not None and self._selected_line is not line:
                    try:
                        self._selected_line.set_color(self._selected_line_prev_color)
                    except Exception:
                        pass
                # 记录并高亮当前线
                self._selected_line = line
                self._selected_line_prev_color = line.get_color()
                line.set_color('#ff9800')  # 橙色
                self.draw_idle()
                return True
        return False

    def _on_press(self, event):
        # 仅左键且在数据区域内
        if event.button != 1 or event.inaxes is None or event.inaxes is not self.axes:
            return
        
        # zoom 模式：记录起点
        if self._mode == 'zoom':
            self._zooming = True
            self._zoom_start = (event.xdata, event.ydata)
            # 创建虚线矩形
            self._zoom_rect = Rectangle(
                (event.xdata, event.ydata), 0, 0,
                linewidth=1, edgecolor='red', facecolor='none',
                linestyle='--'
            )
            self.axes.add_patch(self._zoom_rect)
            self.draw_idle()
            return
        
        # pan 模式：启动平移
        if self._mode == 'pan':
            self.setCursor(Qt.ClosedHandCursor)
            self._panning = True
            self._press_disp = (event.x, event.y)
            self._press_xlim = self.axes.get_xlim()
            self._press_ylim = self.axes.get_ylim()
            self._inv_trans = self.axes.transData.inverted()
            return
        
        # 默认模式：检测标题、线条点击
        # print("canves", type(event.canvas))
        # 先检测标题和 X 轴标签点击
        if self.highlight_title_if_clicked(event):
            return
        # 点击到线则高亮并不进入平移
        if self.highlight_line_if_clicked(event):
            return

    def _on_motion(self, event):
        # zoom 模式：更新矩形框
        if self._zooming and self._zoom_start is not None:
            if event.xdata is None or event.ydata is None:
                return
            x0, y0 = self._zoom_start
            width = event.xdata - x0
            height = event.ydata - y0
            self._zoom_rect.set_width(width)
            self._zoom_rect.set_height(height)
            self.draw_idle()
            return
        
        # pan 模式：平移坐标轴
        if self._panning and self._press_disp is not None:
            # 即使移出数据区（event.inaxes 为 None），也基于显示坐标计算
            if self.cursor().shape() != Qt.ClosedHandCursor:
                self.setCursor(Qt.SizeAllCursor)
            x0_disp, y0_disp = self._press_disp
            x1_disp, y1_disp = event.x, event.y

            # 显示坐标 -> 数据坐标（支持线性/对数坐标）
            x0_data, y0_data = self._inv_trans.transform((x0_disp, y0_disp))
            x1_data, y1_data = self._inv_trans.transform((x1_disp, y1_disp))

            dx = x1_data - x0_data
            dy = y1_data - y0_data

            xl0, xl1 = self._press_xlim
            yl0, yl1 = self._press_ylim

            # 平移：坐标轴范围与鼠标移动方向相反
            self.axes.set_xlim(xl0 - dx, xl1 - dx)
            self.axes.set_ylim(yl0 - dy, yl1 - dy)
            self.draw_idle()

    def _on_release(self, event):
        if event.button != 1:
            return
        
        # zoom 模式：根据框范围缩放
        if self._zooming:
            self._zooming = False
            if self._zoom_rect is not None:
                self._zoom_rect.remove()
                self._zoom_rect = None
            
            if self._zoom_start is not None and event.xdata is not None and event.ydata is not None:
                x0, y0 = self._zoom_start
                x1, y1 = event.xdata, event.ydata
                # 确保左下到右上
                xmin, xmax = min(x0, x1), max(x0, x1)
                ymin, ymax = min(y0, y1), max(y0, y1)
                # 避免缩放范围过小
                if abs(xmax - xmin) > 1e-6 and abs(ymax - ymin) > 1e-6:
                    self.axes.set_xlim(xmin, xmax)
                    self.axes.set_ylim(ymin, ymax)
                    self.draw_idle()
            self._zoom_start = None
            return
        
        # pan 模式：结束平移
        if self._panning:
            if self._mode == 'pan':
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.unsetCursor()  # 还原默认光标
            self._panning = False
            self._press_disp = None
            self._press_xlim = None
            self._press_ylim = None

    def _on_scroll(self, event):
        # 仅在当前坐标轴内滚动才缩放
        if event.inaxes is None or event.inaxes is not self.axes:
            return
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return

        base_scale = 1.2
        # 鼠标上滚放大（范围变小），下滚缩小（范围变大）
        scale = 1 / base_scale if event.button == 'up' else base_scale

        # 可选：Ctrl 只缩放 X，Shift 只缩放 Y
        key = (event.key or '').lower()
        zoom_x = 'shift' not in key
        zoom_y = 'control' not in key and 'ctrl' not in key

        ax = self.axes
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