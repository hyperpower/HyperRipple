from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QCursor
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D


class CanvasCropTool(QObject):
    """Canvas 裁剪工具类 - 可拖动的裁剪框
    
    功能：
    1. 鼠标点击工具栏上 crop 进入 crop 模式
    2. 在 canvas 插入的图片四周画一个框
    3. 框的四条边可以用鼠标拖动以更改位置
    4. 再次点击 crop 按钮退出 crop 模式
    """
    
    # 信号：裁剪完成，参数为裁剪区域的坐标 (x0, y0, x1, y1)
    crop_completed = Signal(float, float, float, float)
    
    # 拖动边的阈值（数据坐标单位）
    EDGE_THRESHOLD = 0.02
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.main_ax = canvas.main_ax
        
        # 裁剪框状态
        self._active = False  # 是否处于 crop 模式
        self._dragging_edge = None  # 当前拖动的边 ('left', 'right', 'top', 'bottom', 'inside')
        self._drag_start = None  # 拖动起点 (数据坐标)
        self._box_start = None  # 拖动开始时裁剪框的坐标
        
        # 裁剪框坐标 (数据坐标) - 初始化为整个图像区域
        self._x0, self._y0 = 0, 0  # 左下角
        self._x1, self._y1 = 1, 1  # 右上角
        
        # 图形元素
        self._crop_rect = None  # 裁剪框矩形边框
        self._crop_rects = []  # 裁剪框外部遮罩矩形列表
        self._handles = []  # 四个边的拖动手柄（Line2D 对象）
        self._init_handles()
    
    def _init_handles(self):
        """初始化拖动手柄"""
        # 四个边的手柄：left, right, bottom, top
        colors = ['#ff0000', '#ff0000', '#00ff00', '#00ff00']  # 红：左右，绿：上下
        for i, color in enumerate(colors):
            handle = Line2D([], [], color=color, linewidth=3, 
                           marker='s', markersize=8, 
                           markerfacecolor=color, markeredgecolor='white',
                           pickradius=5, visible=False)
            self._handles.append(handle)
    
    def set_active(self, active: bool):
        """启用/禁用 crop 模式"""
        self._active = active
        if active:
            self._init_crop_box()
            self._draw_crop_box()
        else:
            self._remove_crop_box()
    
    def is_active(self) -> bool:
        """是否处于 crop 模式"""
        return self._active
    
    def _init_crop_box(self):
        """初始化裁剪框为当前视图范围"""
        xlim = self.main_ax.get_xlim()
        ylim = self.main_ax.get_ylim()
        
        # 处理反向坐标轴
        self._x0, self._x1 = sorted(xlim)
        self._y0, self._y1 = sorted(ylim)
        
        # 稍微缩小一点，让框在图像内部
        x_margin = (self._x1 - self._x0) * 0.1
        y_margin = (self._y1 - self._y0) * 0.1
        self._x0 += x_margin
        self._x1 -= x_margin
        self._y0 += y_margin
        self._y1 -= y_margin
    
    def _draw_crop_box(self):
        """绘制裁剪框和手柄"""
        if not self._active:
            return
        
        # 清除旧的图形
        self._remove_crop_box()
        
        # 获取当前视图范围
        xlim = self.main_ax.get_xlim()
        ylim = self.main_ax.get_ylim()
        x_min, x_max = sorted(xlim)
        y_min, y_max = sorted(ylim)
        
        # 绘制裁剪框外部的浅灰色遮罩（上、下、左、右四个区域）
        shade_color = '#808080'  # 浅灰色
        shade_alpha = 0.5
        
        # 下边区域
        self._add_shade_rect(x_min, y_min, x_max - x_min, self._y0 - y_min, shade_color, shade_alpha)
        # 上边区域
        self._add_shade_rect(x_min, self._y1, x_max - x_min, y_max - self._y1, shade_color, shade_alpha)
        # 左边区域
        self._add_shade_rect(x_min, self._y0, self._x0 - x_min, self._y1 - self._y0, shade_color, shade_alpha)
        # 右边区域
        self._add_shade_rect(self._x1, self._y0, x_max - self._x1, self._y1 - self._y0, shade_color, shade_alpha)
        
        # 绘制裁剪框边框（绿色）
        self._crop_rect = Rectangle(
            (self._x0, self._y0),
            self._x1 - self._x0,
            self._y1 - self._y0,
            linewidth=2, edgecolor='#00ff00',
            facecolor='none',
            linestyle='-', zorder=5
        )
        self.main_ax.add_patch(self._crop_rect)
        
        # 添加四个边的手柄
        self._update_handles()
        for handle in self._handles:
            handle.set_visible(True)
            self.main_ax.add_artist(handle)
        
        self.canvas.draw_idle()
    
    def _add_shade_rect(self, x, y, width, height, color, alpha):
        """添加一个遮罩矩形"""
        if width > 0 and height > 0:
            rect = Rectangle(
                (x, y),
                width,
                height,
                linewidth=0,
                facecolor=color, alpha=alpha,
                zorder=4
            )
            self.main_ax.add_patch(rect)
            self._crop_rects.append(rect)
    
    def _update_handles(self):
        """更新四个拖动手柄的位置"""
        cx = (self._x0 + self._x1) / 2
        cy = (self._y0 + self._y1) / 2
        
        # left handle
        self._handles[0].set_data([self._x0], [cy])
        # right handle
        self._handles[1].set_data([self._x1], [cy])
        # bottom handle
        self._handles[2].set_data([cx], [self._y0])
        # top handle
        self._handles[3].set_data([cx], [self._y1])
    
    def _remove_crop_box(self):
        """移除裁剪框和手柄"""
        if self._crop_rect is not None:
            self._crop_rect.remove()
            self._crop_rect = None
        
        # 移除外部遮罩矩形
        for rect in self._crop_rects:
            if rect.axes is not None:
                rect.remove()
        self._crop_rects = []
        
        for handle in self._handles:
            if handle.axes is not None:
                handle.remove()
        
        self.canvas.draw_idle()
    
    def _get_edge_at_position(self, x, y) -> str:
        """检测给定位置最近的边或内部"""
        if x is None or y is None:
            return None
        
        # 计算到各边的距离
        dist_left = abs(x - self._x0)
        dist_right = abs(x - self._x1)
        dist_bottom = abs(y - self._y0)
        dist_top = abs(y - self._y1)
        
        # 获取坐标轴范围用于计算相对阈值
        xlim = self.main_ax.get_xlim()
        ylim = self.main_ax.get_ylim()
        x_range = abs(xlim[1] - xlim[0])
        y_range = abs(ylim[1] - ylim[0])
        
        # 动态阈值
        x_threshold = x_range * self.EDGE_THRESHOLD
        y_threshold = y_range * self.EDGE_THRESHOLD
        
        # 检查是否点击了某个边（手柄位置）
        cx = (self._x0 + self._x1) / 2
        cy = (self._y0 + self._y1) / 2
        
        # 检查左右边的手柄
        if abs(x - self._x0) < x_threshold and abs(y - cy) < y_threshold * 3:
            return 'left'
        if abs(x - self._x1) < x_threshold and abs(y - cy) < y_threshold * 3:
            return 'right'
        
        # 检查上下边的手柄
        if abs(y - self._y0) < y_threshold and abs(x - cx) < x_threshold * 3:
            return 'bottom'
        if abs(y - self._y1) < y_threshold and abs(x - cx) < x_threshold * 3:
            return 'top'
        
        # 检查是否在框内（用于整体移动）
        x_inside = min(self._x0, self._x1) <= x <= max(self._x0, self._x1)
        y_inside = min(self._y0, self._y1) <= y <= max(self._y0, self._y1)
        if x_inside and y_inside:
            return 'inside'
        
        return None
    
    def on_press(self, event):
        """处理鼠标按下事件"""
        if not self._active:
            return
        
        if event.button != 1 or event.inaxes is not self.main_ax:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        # 检测点击位置
        edge = self._get_edge_at_position(event.xdata, event.ydata)
        if edge is not None:
            self._dragging_edge = edge
            self._drag_start = (event.xdata, event.ydata)
            self._box_start = (self._x0, self._y0, self._x1, self._y1)
            
            # 更改光标
            if edge == 'left' or edge == 'right':
                self.canvas.setCursor(Qt.SizeHorCursor)
            elif edge == 'bottom' or edge == 'top':
                self.canvas.setCursor(Qt.SizeVerCursor)
            elif edge == 'inside':
                self.canvas.setCursor(Qt.SizeAllCursor)
    
    def on_motion(self, event):
        """处理鼠标移动事件"""
        if not self._active:
            return
        
        # 更新光标（悬停时）
        if self._dragging_edge is None and event.inaxes is self.main_ax:
            if event.xdata is not None and event.ydata is not None:
                edge = self._get_edge_at_position(event.xdata, event.ydata)
                if edge == 'left' or edge == 'right':
                    self.canvas.setCursor(Qt.SizeHorCursor)
                elif edge == 'bottom' or edge == 'top':
                    self.canvas.setCursor(Qt.SizeVerCursor)
                elif edge == 'inside':
                    self.canvas.setCursor(Qt.SizeAllCursor)
                else:
                    self.canvas.setCursor(Qt.ArrowCursor)
        
        # 拖动处理
        if self._dragging_edge is None or self._drag_start is None:
            return
        
        if event.xdata is None or event.ydata is None:
            return
        
        dx = event.xdata - self._drag_start[0]
        dy = event.ydata - self._drag_start[1]
        
        x0, y0, x1, y1 = self._box_start
        
        if self._dragging_edge == 'left':
            self._x0 = min(x0 + dx, self._x1 - 0.01)
        elif self._dragging_edge == 'right':
            self._x1 = max(x1 + dx, self._x0 + 0.01)
        elif self._dragging_edge == 'bottom':
            self._y0 = min(y0 + dy, self._y1 - 0.01)
        elif self._dragging_edge == 'top':
            self._y1 = max(y1 + dy, self._y0 + 0.01)
        elif self._dragging_edge == 'inside':
            # 整体移动
            self._x0 = x0 + dx
            self._x1 = x1 + dx
            self._y0 = y0 + dy
            self._y1 = y1 + dy
        
        self._update_crop_box()
    
    def _update_crop_box(self):
        """更新裁剪框显示"""
        # 重新绘制整个裁剪框（包括外部遮罩）
        self._draw_crop_box()
    
    def on_release(self, event):
        """处理鼠标释放事件"""
        if self._dragging_edge is not None:
            self._dragging_edge = None
            self._drag_start = None
            self._box_start = None
            self.canvas.setCursor(Qt.ArrowCursor)
    
    def get_crop_bounds(self) -> tuple:
        """获取裁剪框的边界坐标"""
        # 确保返回有序坐标
        x0, x1 = sorted([self._x0, self._x1])
        y0, y1 = sorted([self._y0, self._y1])
        return (x0, y0, x1, y1)
    
    def apply_crop(self):
        """应用裁剪，发射裁剪完成信号"""
        if not self._active:
            return
        
        bounds = self.get_crop_bounds()
        self.crop_completed.emit(*bounds)