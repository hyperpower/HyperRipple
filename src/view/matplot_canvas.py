from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseEvent


class MatplotCanvas(FigureCanvas):
    def __init__(self, node, matfig = None):
        self._figure_node = node
        if matfig is not None:
            self.fig = matfig
        else:
            self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        # self.axes.set_aspect("equal")
        # self.fig.subplots_adjust(left=0.1, right=0.9, bottom=0.12, top=0.92)
        super(MatplotCanvas, self).__init__(self.fig)
        
        
        # 平移相关状态
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
        # 先检测标题和 X 轴标签点击
        if self.highlight_title_if_clicked(event):
            return
        # 点击到线则高亮并不进入平移
        if self.highlight_line_if_clicked(event):
            return
        # 仅当在数据区域内按下左键时启动平移
        if event.button != 1 or event.inaxes is None or event.inaxes is not self.axes:
            return
        self._panning = True
        self._press_disp = (event.x, event.y)
        self._press_xlim = self.axes.get_xlim()
        self._press_ylim = self.axes.get_ylim()
        self._inv_trans = self.axes.transData.inverted()

    def _on_motion(self, event):
        if not self._panning or self._press_disp is None:
            return
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