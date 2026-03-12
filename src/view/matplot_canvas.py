from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseEvent
from view.canvas_zoom_tool import CanvasZoomTool
from view.canvas_crop_tool import CanvasCropTool


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
        # self.main_ax.set_aspect("equal")
        # self.fig.subplots_adjust(left=0.1, right=0.9, bottom=0.12, top=0.92)
        super(MatplotCanvas, self).__init__(self.fig)
        
        # 初始化 Zoom 工具
        self.zoom_tool = CanvasZoomTool(self)
        # 初始化 Crop 工具
        self.crop_tool = CanvasCropTool(self)
        self.crop_tool.crop_completed.connect(self._on_crop_completed)
        
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
        ax, = self.fig.axes if self.fig.axes else (None,)
        self._inv_trans = ax.transData.inverted() if ax is not None else None

        # 标题高亮状态
        self._title_highlighted = False
        
        # 初始视图状态（用于 home 按钮恢复）
        self._initial_xlim = None
        self._initial_ylim = None
        self._has_initial_view = False

        # 连接事件
        self._cid_press = self.mpl_connect('button_press_event', self._on_press)
        self._cid_motion = self.mpl_connect('motion_notify_event', self._on_motion)
        self._cid_release = self.mpl_connect('button_release_event', self._on_release)
        # 鼠标滚轮缩放数据区域
        self._cid_scroll = self.mpl_connect('scroll_event', self._on_scroll)
        # 选中线的状态
        self._selected_line = None
        self._selected_line_prev_color = None
    
    def set_mode(self, mode: str | None):
        """设置当前交互模式：'pan' 或 None。"""
        self._mode = mode
    
    def set_initial_view(self, xlim=None, ylim=None):
        """
        设置初始视图范围。
        如果没有提供参数，则使用当前视图范围作为初始视图。
        如果没有数据（xlim/ylim为None），使用默认范围（0-100）。
        """
        if xlim is None:
            xlim = self.main_ax.get_xlim()
        if ylim is None:
            ylim = self.main_ax.get_ylim()
        
        # 检查是否是默认范围（没有数据时）
        if xlim[0] == 0.0 and xlim[1] == 1.0 and ylim[0] == 0.0 and ylim[1] == 1.0:
            # 使用默认范围 0-100
            self._initial_xlim = (0, 100)
            self._initial_ylim = (0, 100)
        else:
            self._initial_xlim = xlim
            self._initial_ylim = ylim
        
        self._has_initial_view = True
    
    def reset_view(self):
        """
        重置视图到初始状态。
        如果没有设置初始视图，使用默认范围（0-100）。
        """
        if self._has_initial_view and self._initial_xlim is not None and self._initial_ylim is not None:
            self.main_ax.set_xlim(self._initial_xlim)
            self.main_ax.set_ylim(self._initial_ylim)
        else:
            # 使用默认范围 0-100
            self.main_ax.set_xlim(0, 100)
            self.main_ax.set_ylim(0, 100)
        self.draw_idle()
    
    def _render_figure_from_node(self, node):
        """根据 FigureNode 的属性渲染图形内容。"""
        self.main_ax.clear()
        # self.fig.set_figwidth(node["width"].value)
        # self.fig.set_figheight(node["height"].value)
        # self.fig.set_dpi(50)
        self.fig.suptitle(node["title"].value)

        for ax in node.iter_by_class("AxesNode"):
            self.main_ax.set_xlabel(ax["xlabel"].value)
            self.main_ax.set_ylabel(ax["ylabel"].value)
            self.main_ax.set_title(ax["title"].value)
            for data_node in ax.iter_by_class("DataNode"):
                x_data = data_node["x"].value
                y_data = data_node["y"].value
                self.main_ax.plot(x_data, y_data, label=data_node["label"].value)

        # 设置初始视图范围（在绘制数据后）
        self._update_initial_view()
        
        # self.main_ax.set_xlim(node["Axes"]["xlim_min"].value, node["Axes"]["xlim_max"].value)
        # self.main_ax.set_ylim(node["Axes"]["ylim_min"].value, node["Axes"]["ylim_max"].value)
        # Get data from DataNode children
        self.main_ax.grid(True)
    
    def _update_initial_view(self):
        """
        更新初始视图范围。
        如果还没有设置初始视图，则根据当前数据设置。
        """
        if not self._has_initial_view:
            xlim = self.main_ax.get_xlim()
            ylim = self.main_ax.get_ylim()
            self.set_initial_view(xlim, ylim)


    def highlight_title_if_clicked(self, event) -> bool:
        """
        判断是否点击了标题；若点击，则显示/切换标题边框并返回 True，否则返回 False。
        """
        title_obj = self.main_ax.title  # Text 对象
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
        if event.inaxes is None or event.inaxes is not self.main_ax:
            return False
        for line in self.main_ax.get_lines():
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
        print(f"Mouse press at ({event.x}, {event.y}) in canvas coords, "
              f"data coords ({event.xdata}, {event.ydata}), "
              f"inaxes: {event.inaxes}")
        # 仅左键且在数据区域内
        if event.button != 1 or event.inaxes is None or event.inaxes is not self.main_ax:
            return

        if self._mode == 'zoom':
            self.zoom_tool.on_press(event)
        elif self._mode == 'crop':
            self.crop_tool.on_press(event)
            return  # crop 模式只处理拖动，不处理其他
        elif self._mode == 'pan':
            self._handle_pan_press(event)
        elif self._mode == 'add_point':
            self._handle_add_point_press(event)
        elif self._mode == 'brush':
            self._handle_brush_press(event)
        else:
            self._handle_default_press(event)


    def _handle_pan_press(self, event):
        # pan 模式：启动平移
        self.setCursor(Qt.ClosedHandCursor)
        self._panning = True
        self._press_disp = (event.x, event.y)
        self._press_xlim = self.main_ax.get_xlim()
        self._press_ylim = self.main_ax.get_ylim()
        self._inv_trans = self.main_ax.transData.inverted()

    def _handle_add_point_press(self, event):
        # 在数据区域点击添加点
        if event.xdata is not None and event.ydata is not None:
            self.main_ax.plot(event.xdata, event.ydata, marker='o', color='red')
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
        self._brush_scatter = self.main_ax.scatter(
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
    

    def _on_motion(self, event):
        if self._mode == 'zoom':
            self.zoom_tool.on_motion(event)
        elif self._mode == 'crop':
            self.crop_tool.on_motion(event)
            return  # crop 模式只处理拖动
        elif self._mode == 'pan':
            self._handle_pan_motion(event)
        elif self._mode == 'brush':
            self._handle_brush_motion(event)


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
            self.main_ax.set_xlim(xl0 - dx, xl1 - dx)
            self.main_ax.set_ylim(yl0 - dy, yl1 - dy)
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
            self.zoom_tool.on_release(event)
        elif self._mode == 'crop':
            self.crop_tool.on_release(event)
            return  # crop 模式只处理拖动
        elif self._mode == 'pan':
            self._handle_pan_release(event)
        elif self._mode == 'brush':
            self._handle_brush_release(event)
    

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
        if event.inaxes is None or event.inaxes is not self.main_ax:
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
        """处理裁剪完成事件，由外部连接信号处理"""
        # 此方法可由外部连接 crop_tool.crop_completed 信号来调用
        # 默认实现：打印裁剪区域信息
        print(f"Crop area selected: ({x0}, {y0}) to ({x1}, {y1})")
