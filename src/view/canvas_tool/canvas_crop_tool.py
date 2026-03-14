import numpy as np
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QCursor
from matplotlib.patches import Rectangle, Circle


class CanvasCropTool(QObject):
    """Canvas 裁剪工具类 - 可拖动的裁剪框
    """
    
    # 信号：裁剪完成，参数为裁剪区域的坐标 (x0, y0, x1, y1)
    crop_completed = Signal(float, float, float, float)
    
    # 信号：裁剪框变化，参数为裁剪区域的坐标 (x0, y0, x1, y1)
    cropbox_changed = Signal(float, float, float, float)
    
    # 拖动边的阈值（数据坐标单位）
    EDGE_THRESHOLD = 0.02
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.main_ax = canvas.main_ax
        
        # 裁剪框状态
        self._active = False  # 是否处于 crop 模式
        self._dragging_edge = None  # 当前拖动的边或角
        # 边：'left', 'right', 'top', 'bottom', 'inside'
        # 角：'top-left', 'top-right', 'bottom-left', 'bottom-right'
        self._drag_start = None  # 拖动起点 (数据坐标)
        self._box_start = None  # 拖动开始时裁剪框的坐标
        
        # 裁剪框坐标 (数据坐标) - 初始化为整个图像区域
        self._x0, self._y0 = 0, 0  # 左下角
        self._x1, self._y1 = 1, 1  # 右上角
        
        # 图形元素
        self._crop_rect = None  # 裁剪框矩形边框
        self._crop_rects = []  # 裁剪框外部遮罩矩形列表
        self._handles = []  # 8 个拖动手柄（4 个边 Rectangle + 4 个角 Circle）
    
    def _create_handles(self):
        """创建拖动手柄 - 根据裁剪框尺寸动态计算手柄大小
        
        返回 8 个手柄：
        - 索引 0-3: 4 个边手柄（Rectangle）- 左、右、下、上
        - 索引 4-7: 4 个角手柄（Circle）- 左上、右上、左下、右下
        """
        # 计算裁剪框的宽度和高度
        box_width = abs(self._x1 - self._x0)
        box_height = abs(self._y1 - self._y0)
        
        # 手柄长度为所在边长度的 0.2 倍
        # 左右边手柄的高度（垂直方向）
        left_right_handle_height = box_height * 0.2
        # 上下边手柄的宽度（水平方向）
        top_bottom_handle_width = box_width * 0.2
        
        # 手柄宽度/高度为长度的 0.1 倍（间隔）
        handle_thickness = max(left_right_handle_height, top_bottom_handle_width) * 0.1
        
        # 角手柄半径 - 与边手柄厚度相同
        corner_handle_radius = handle_thickness
        
        handles = []
        
        # === 4 个边手柄（Rectangle）===
        edge_colors = ['#ff0000', '#ff0000', '#00ff00', '#00ff00']  # 红：左右，绿：上下
        
        # left handle - 垂直长条
        handles.append(Rectangle(
            (0, 0),
            handle_thickness, left_right_handle_height,
            linewidth=0,
            facecolor=edge_colors[0],
            zorder=6,
            visible=True
        ))
        # right handle - 垂直长条
        handles.append(Rectangle(
            (0, 0),
            handle_thickness, left_right_handle_height,
            linewidth=0,
            facecolor=edge_colors[1],
            zorder=6,
            visible=True
        ))
        # bottom handle - 水平长条
        handles.append(Rectangle(
            (0, 0),
            top_bottom_handle_width, handle_thickness,
            linewidth=0,
            facecolor=edge_colors[2],
            zorder=6,
            visible=True
        ))
        # top handle - 水平长条
        handles.append(Rectangle(
            (0, 0),
            top_bottom_handle_width, handle_thickness,
            linewidth=0,
            facecolor=edge_colors[3],
            zorder=6,
            visible=True
        ))
        
        # === 4 个角手柄（Circle）===
        corner_color = '#0000ff'  # 蓝色
        
        # top-left corner
        handles.append(Circle(
            (0, 0),  # 初始位置，后续会更新
            corner_handle_radius,
            linewidth=0,
            facecolor=corner_color,
            zorder=6,
            visible=True
        ))
        # top-right corner
        handles.append(Circle(
            (0, 0),
            corner_handle_radius,
            linewidth=0,
            facecolor=corner_color,
            zorder=6,
            visible=True
        ))
        # bottom-left corner
        handles.append(Circle(
            (0, 0),
            corner_handle_radius,
            linewidth=0,
            facecolor=corner_color,
            zorder=6,
            visible=True
        ))
        # bottom-right corner
        handles.append(Circle(
            (0, 0),
            corner_handle_radius,
            linewidth=0,
            facecolor=corner_color,
            zorder=6,
            visible=True
        ))
        
        return handles
    
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
        
        # 创建并添加四个边的手柄
        self._handles = self._create_handles()
        self._update_handles()
        for handle in self._handles:
            self.main_ax.add_patch(handle)
        
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
        """更新 8 个拖动手柄的位置
        
        索引 0-3: 4 个边手柄（Rectangle）- 左、右、下、上
        索引 4-7: 4 个角手柄（Circle）- 左上、右上、左下、右下
        """
        cx = (self._x0 + self._x1) / 2
        cy = (self._y0 + self._y1) / 2
        
        # === 更新 4 个边手柄（Rectangle）===
        left_width = self._handles[0].get_width()
        left_height = self._handles[0].get_height()
        right_width = self._handles[1].get_width()
        right_height = self._handles[1].get_height()
        bottom_width = self._handles[2].get_width()
        bottom_height = self._handles[2].get_height()
        top_width = self._handles[3].get_width()
        top_height = self._handles[3].get_height()
        
        # 手柄间隔 = 手柄长度 * 0.1
        left_gap = left_height * 0.1
        top_gap = top_height * 0.1
        
        # left handle - 在左边外侧，垂直居中
        self._handles[0].set_x(self._x0 - left_width - left_gap)
        self._handles[0].set_y(cy - left_height / 2)
        
        # right handle - 在右边外侧，垂直居中
        self._handles[1].set_x(self._x1 + left_gap)
        self._handles[1].set_y(cy - right_height / 2)
        
        # bottom handle - 在下边外侧，水平居中
        self._handles[2].set_x(cx - bottom_width / 2)
        self._handles[2].set_y(self._y0 - bottom_height - top_gap)
        
        # top handle - 在上边外侧，水平居中
        self._handles[3].set_x(cx - top_width / 2)
        self._handles[3].set_y(self._y1 + top_gap)
        
        # === 更新 4 个角手柄（Circle）===
        # 角手柄中心直接在角点上
        # top-left corner - 左上角
        self._handles[4].center = (self._x0, self._y1)
        # top-right corner - 右上角
        self._handles[5].center = (self._x1, self._y1)
        # bottom-left corner - 左下角
        self._handles[6].center = (self._x0, self._y0)
        # bottom-right corner - 右下角
        self._handles[7].center = (self._x1, self._y0)
    
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
            try:
                handle.remove()
            except Exception:
                pass  # 如果已经移除则忽略
        self._handles = []
        
        self.canvas.draw_idle()
    
    def _get_edge_at_position(self, x, y) -> str:
        """检测给定位置最近的边或角或内部（包括手柄区域）
        
        返回：
        - 边：'left', 'right', 'top', 'bottom'
        - 角：'top-left', 'top-right', 'bottom-left', 'bottom-right'
        - 内部：'inside'
        - 无：None
        """
        if x is None or y is None:
            return None
        
        cx = (self._x0 + self._x1) / 2
        cy = (self._y0 + self._y1) / 2
        
        # 计算裁剪框尺寸
        box_width = abs(self._x1 - self._x0)
        box_height = abs(self._y1 - self._y0)
        
        # 边手柄尺寸
        left_right_handle_height = box_height * 0.2
        top_bottom_handle_width = box_width * 0.2
        handle_thickness = max(left_right_handle_height, top_bottom_handle_width) * 0.1
        handle_gap = max(left_right_handle_height, top_bottom_handle_width) * 0.1
        
        # 角手柄半径和间隔
        corner_radius = handle_thickness * 1.5  # 角手柄检测半径稍大一些
        
        # === 检查 4 个边手柄 ===
        # left handle
        left_x = self._x0 - handle_thickness - handle_gap
        left_y = cy - left_right_handle_height / 2
        if (left_x <= x <= left_x + handle_thickness and 
            left_y <= y <= left_y + left_right_handle_height):
            return 'left'
        # right handle
        right_x = self._x1 + handle_gap
        right_y = cy - left_right_handle_height / 2
        if (right_x <= x <= right_x + handle_thickness and 
            right_y <= y <= right_y + left_right_handle_height):
            return 'right'
        # bottom handle
        bottom_x = cx - top_bottom_handle_width / 2
        bottom_y = self._y0 - handle_thickness - handle_gap
        if (bottom_x <= x <= bottom_x + top_bottom_handle_width and 
            bottom_y <= y <= bottom_y + handle_thickness):
            return 'bottom'
        # top handle
        top_x = cx - top_bottom_handle_width / 2
        top_y = self._y1 + handle_gap
        if (top_x <= x <= top_x + top_bottom_handle_width and 
            top_y <= y <= top_y + handle_thickness):
            return 'top'
        
        # === 检查 4 个角手柄（圆形区域）===
        # 角手柄检测半径
        detect_radius = corner_radius
        
        # top-left - 中心在角点上
        if np.hypot(x - self._x0, y - self._y1) <= detect_radius:
            return 'top-left'
        # top-right
        if np.hypot(x - self._x1, y - self._y1) <= detect_radius:
            return 'top-right'
        # bottom-left
        if np.hypot(x - self._x0, y - self._y0) <= detect_radius:
            return 'bottom-left'
        # bottom-right
        if np.hypot(x - self._x1, y - self._y0) <= detect_radius:
            return 'bottom-right'
        
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
            elif edge in ['top-left', 'bottom-right']:
                self.canvas.setCursor(Qt.SizeBDiagCursor)  # 反对角线（↗↙）
            elif edge in ['top-right', 'bottom-left']:
                self.canvas.setCursor(Qt.SizeFDiagCursor)  # 正对角线（↖↘）
    
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
                elif edge in ['top-left', 'bottom-right']:
                    self.canvas.setCursor(Qt.SizeBDiagCursor)  # 反对角线（↗↙）
                elif edge in ['top-right', 'bottom-left']:
                    self.canvas.setCursor(Qt.SizeFDiagCursor)  # 正对角线（↖↘）
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
        elif self._dragging_edge == 'top-left':
            # 左上角：同时改变 x0 和 y1
            self._x0 = min(x0 + dx, self._x1 - 0.01)
            self._y1 = max(y1 + dy, self._y0 + 0.01)
        elif self._dragging_edge == 'top-right':
            # 右上角：同时改变 x1 和 y1
            self._x1 = max(x1 + dx, self._x0 + 0.01)
            self._y1 = max(y1 + dy, self._y0 + 0.01)
        elif self._dragging_edge == 'bottom-left':
            # 左下角：同时改变 x0 和 y0
            self._x0 = min(x0 + dx, self._x1 - 0.01)
            self._y0 = min(y0 + dy, self._y1 - 0.01)
        elif self._dragging_edge == 'bottom-right':
            # 右下角：同时改变 x1 和 y0
            self._x1 = max(x1 + dx, self._x0 + 0.01)
            self._y0 = min(y0 + dy, self._y1 - 0.01)
        
        self._update_crop_box()
    
    def _update_crop_box(self):
        """更新裁剪框显示"""
        # 重新绘制整个裁剪框（包括外部遮罩）
        self._draw_crop_box()
        # 发射 cropbox 变化信号
        self.cropbox_changed.emit(*self.get_crop_bounds())
    
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