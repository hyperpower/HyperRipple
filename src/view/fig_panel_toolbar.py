from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon

from view.view_helper import createThemedPixmap, createEmptyIcon


class FigPanelToolbar(QToolBar):
    """Figure 面板的工具栏类，继承自 QToolBar。"""
    
    def __init__(self, canvas, fig_panel, parent=None):
        super().__init__("工具栏", parent)
        self.canvas = canvas
        self.fig_panel = fig_panel
        self._current_node = None
        self.actions = {}
        self._dynamic_actions = []  # 动态添加的按钮
        
        self.setMovable(False)
        self._init_actions()
    
    def set_node(self, node):
        """设置当前节点并更新工具栏按钮。"""
        self._current_node = node
        self.update_actions_from_node()
    
    def _create_tool_action(self, key: str, icon_path: str, text: str, callback):
        """创建工具栏按钮的通用方法。"""
        icon = QIcon()
        icon.addPixmap(createThemedPixmap(icon_path), QIcon.Normal, QIcon.Off)
        icon.addPixmap(createThemedPixmap(icon_path, color='#007AFF'), QIcon.Normal, QIcon.On)
        action = QAction(icon, text, self)
        action.setCheckable(True)
        action.triggered.connect(callback)
        self.addAction(action)
        self.actions[key] = action
    
    def _create_dynamic_action(self, icon_path: str, action_name: str, handler):
        """创建动态工具栏按钮。"""
        if icon_path:
            icon = QIcon()
            icon_path = icon_path if icon_path.startswith("/") else f"asset/icons/{icon_path}"
            icon.addPixmap(createThemedPixmap(icon_path), QIcon.Normal, QIcon.Off)
            icon.addPixmap(createThemedPixmap(icon_path, color='#007AFF'), QIcon.Normal, QIcon.On)
        else:
            icon = createEmptyIcon()
        
        action = QAction(icon, action_name, self)
        action.triggered.connect(handler)
        self.addAction(action)
        self._dynamic_actions.append(action)
    
    def _clear_dynamic_actions(self):
        """清除所有动态添加的工具栏按钮。"""
        for action in self._dynamic_actions:
            self.removeAction(action)
        self._dynamic_actions.clear()
    
    def update_actions_from_node(self):
        """根据当前节点的 allowed_actions 更新工具栏按钮。"""
        self._clear_dynamic_actions()
        
        if self._current_node is None:
            return
        
        allowed_actions = self._current_node.allowed_actions()
        for icon_path, action_name, handler in allowed_actions:
            if handler is not None:
                self._create_dynamic_action(icon_path, action_name, handler)
    
    def _init_actions(self):
        """初始化所有工具栏按钮。"""
        self._create_tool_action('zoom', "asset/icons/zoom.svg", "Zoom", self._on_zoom_clicked)
        self._create_tool_action('pan', "asset/icons/hand.svg", "Pan", self._on_pan_clicked)
        self._create_tool_action('add_point', "asset/icons/add_point.svg", "Add Point", self._on_add_point_clicked)
        self._create_tool_action('brush', "asset/icons/brush.svg", "Brush", self._on_brush_clicked)
        self._create_tool_action('crop', "asset/icons/crop.svg", "Crop", self._on_crop_clicked)
    
    def reset_other_actions(self, key):
        """重置其他按钮的状态。"""
        for k, action in self.actions.items():
            if k != key:
                action.setChecked(False)
    
    def _on_zoom_clicked(self):
        """缩放工具点击事件。"""
        if self.actions['zoom'].isChecked():
            self.reset_other_actions('zoom')
            self.fig_panel.set_mode('zoom')
            self.canvas.set_mode('zoom')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.fig_panel.set_mode(None)
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_pan_clicked(self):
        """平移工具点击事件。"""
        if self.actions['pan'].isChecked():
            self.reset_other_actions('pan')
            self.fig_panel.set_mode('pan')
            self.canvas.set_mode('pan')
            self.canvas.setCursor(Qt.OpenHandCursor)
        else:
            self.fig_panel.set_mode(None)
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_add_point_clicked(self):
        """添加点工具点击事件。"""
        if self.actions['add_point'].isChecked():
            self.reset_other_actions('add_point')
            self.fig_panel.set_mode('add_point')
            self.canvas.set_mode('add_point')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.fig_panel.set_mode(None)
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_brush_clicked(self):
        """笔刷工具点击事件。"""
        if self.actions['brush'].isChecked():
            self.reset_other_actions('brush')
            self.fig_panel.set_mode('brush')
            self.canvas.set_mode('brush')
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.fig_panel.set_mode(None)
            self.canvas.set_mode(None)
            self.canvas.unsetCursor()
    
    def _on_crop_clicked(self):
        """裁剪工具点击事件。"""
        if self.actions['crop'].isChecked():
            self.reset_other_actions('crop')
            self.fig_panel.set_mode('crop')
            self.canvas.set_mode('crop')
            self.canvas.crop_tool.set_active(True)
            self.canvas.setCursor(Qt.CrossCursor)
        else:
            self.fig_panel.set_mode(None)
            self.canvas.set_mode(None)
            self.canvas.crop_tool.set_active(False)
            self.canvas.unsetCursor()
