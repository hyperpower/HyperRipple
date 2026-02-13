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
        self._zoom_text = None  # Zoom 框内的文字
        # brush
        self._brushing = False
        self._brush_points = []
        self._brush_scatter = None
        self._brush_last_disp = None
        self._brush_size = 120  # points^2
        self._brush_spacing = 6  # pixels
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
        print(f"Mouse press at ({event.x}, {event.y}) in canvas coords, "              f"data coords ({event.xdata}, {event.ydata}), "
              f"inaxes: {event.inaxes}")
        # 仅左键且在数据区域内
        if event.button != 1 or event.inaxes is None or event.inaxes is not self.axes:
            return

        if self._mode == 'zoom':
            self._handle_zoom_press(event)
        elif self._mode == 'pan':
            self._handle_pan_press(event)
        elif self._mode == 'add_point':
            self._handle_add_point_press(event)
        elif self._mode == 'brush':
            self._handle_brush_press(event)
        else:
            self._handle_default_press(event)

    def _handle_zoom_press(self, event):
        # zoom 模式：记录起点
        self._zooming = True
        self._zoom_start = (event.xdata, event.ydata)
        # 创建虚线矩形
        self._zoom_rect = Rectangle(
            (event.xdata, event.ydata), 0, 0,
            linewidth=1, edgecolor='red', facecolor='none',
            linestyle='--'
        )
        self.axes.add_patch(self._zoom_rect)
        # 创建文字对象
        self._zoom_text = self.axes.text(event.xdata, event.ydata, "Zoom", color='red',
                                        ha='center', va='center', fontsize=8, zorder=10, visible=True)
        self.draw_idle()

    def _handle_pan_press(self, event):
        # pan 模式：启动平移
        self.setCursor(Qt.ClosedHandCursor)
        self._panning = True
        self._press_disp = (event.x, event.y)
        self._press_xlim = self.axes.get_xlim()
        self._press_ylim = self.axes.get_ylim()
        self._inv_trans = self.axes.transData.inverted()

    def _handle_add_point_press(self, event):
        # 在数据区域点击添加点
        if event.xdata is not None and event.ydata is not None:
            self.axes.plot(event.xdata, event.ydata, marker='o', color='red')
            self.draw_idle()
            print("after draw idel, added point at data coords ({}, {})".format(event.xdata, event.ydata))

    def _handle_default_press(self, event):
        # 默认模式：检测标题、线条点击
        # print("canves", type(event.canvas))
        # 先检测标题和 X 轴标签点击
        if self.highlight_title_if_clicked(event):
            return
        # 点击到线则高亮并不进入平移
        if self.highlight_line_if_clicked(event):
            return

    def _handle_brush_press(self, event):
        # brush 模式：开始笔刷选择
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
        self._brush_scatter = self.axes.scatter(
            [], [], s=self._brush_size, c='#4caf50', alpha=0.25,
            edgecolors='none', zorder=5
        )
        self._brush_last_disp = (event.x, event.y)
        self._add_brush_point(event)
        self.draw_idle()

    def _add_brush_point(self, event):
        if event.xdata is None or event.ydata is None:
            return
        self._brush_points.append((event.xdata, event.ydata))
        if self._brush_scatter is not None:
            self._brush_scatter.set_offsets(self._brush_points)
    
    def is_reverse_yaxis(self) -> bool:
        """判断当前坐标轴是否为反向 Y 轴（图像坐标系）。"""
        ylim = self.axes.get_ylim()
        return ylim[0] > ylim[1]
    
    def is_reverse_xaxis(self) -> bool:
        """判断当前坐标轴是否为反向 X 轴。"""
        xlim = self.axes.get_xlim()
        return xlim[0] > xlim[1]

    def _on_motion(self, event):
        if self._mode == 'zoom':
            self._handle_zoom_motion(event)
        elif self._mode == 'pan':
            self._handle_pan_motion(event)
        elif self._mode == 'brush':
            self._handle_brush_motion(event)

    def _handle_zoom_motion(self, event):
        if self._zooming and self._zoom_start is not None:
            if event.xdata is None or event.ydata is None:
                return
            x0, y0 = self._zoom_start
            width  = event.xdata - x0
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
            self.draw_idle()

    def _handle_pan_motion(self, event):
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

    def _handle_brush_motion(self, event):
        if self._brushing:
            if event.xdata is None or event.ydata is None:
                return
            if self._brush_last_disp is None:
                self._brush_last_disp = (event.x, event.y)
                self._add_brush_point(event)
                self.draw_idle()
                return
            x0_disp, y0_disp = self._brush_last_disp
            dx = event.x - x0_disp
            dy = event.y - y0_disp
            if (dx * dx + dy * dy) >= (self._brush_spacing * self._brush_spacing):
                self._brush_last_disp = (event.x, event.y)
                self._add_brush_point(event)
                self.draw_idle()

    def _on_release(self, event):
        if event.button != 1:
            return
        if self._mode == 'zoom':
            self._handle_zoom_release(event)
        elif self._mode == 'pan':
            self._handle_pan_release(event)
        elif self._mode == 'brush':
            self._handle_brush_release(event)
    
    def __abs_fraction_on_axis(self, v0, v1, axis = "x") -> float:
        """计算 v0 到 v1 在指定轴（x 或 y）上的绝对比例（0 到 1）。"""
        if axis == "x":
            ax_min, ax_max = self.axes.get_xlim()
        else:
            ax_min, ax_max = self.axes.get_ylim()
        if ax_max == ax_min:
            return 0.0
        return abs(v1 - v0) / abs(ax_max - ax_min)

    def _handle_zoom_release(self, event):
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
            if self.__abs_fraction_on_axis(x0, x1, "x") < 0.05 \
                or self.__abs_fraction_on_axis(y0, y1, "y") < 0.05:
                # 如果缩放区域太小，则认为是误操作，取消缩放
                self._zoom_start = None
                self.draw_idle()
                return
            # Zoom out 
            # Zoom in 
            if self.is_reverse_xaxis():
                x0, x1 = max(x0, x1), min(x0, x1)
            if self.is_reverse_yaxis():
                y0, y1 = max(y0, y1), min(y0, y1)
            self.axes.set_xlim(x0, x1)
            self.axes.set_ylim(y0, y1)
            self.draw_idle()
        self._zoom_start = None

    def _handle_pan_release(self, event):
        if self._panning:
            if self._mode == 'pan':
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.unsetCursor()  # 还原默认光标
            self._panning = False
            self._press_disp = None
            self._press_xlim = None
            self._press_ylim = None

    def _handle_brush_release(self, event):
        if self._brushing:
            self._brushing = False
            self._brush_last_disp = None

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