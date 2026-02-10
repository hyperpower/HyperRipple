from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QTreeView,
    QPushButton, QHBoxLayout, QStyledItemDelegate, QProgressBar, QStyle,
    QLabel, QSplitter, QTabWidget, QProxyStyle, QDockWidget, QToolBar
)
from view.aspect_ratio_container import AspectRatioContainer

class TabPanel(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabBar().setExpanding(False)
        self.tabBar().setUsesScrollButtons(True) 

    def close_tab(self, index):
        self.removeTab(index)
    
    def update_figure_aspect_ratio(self, canvas, aspect_ratio):
        """Update the aspect ratio of the tab containing the given canvas."""
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, AspectRatioContainer) and widget._canvas == canvas:
                widget.setAspectRatio(aspect_ratio)
                break

    def add_new_figure_tab(self, canvas, title):
        """
        Wrap the canvas with AspectRatioContainer so the canvas scales to fit the tab
        while preserving the canvas' figure aspect ratio and staying centered.
        """
        aspect = 1.0
        try:
            aspect = canvas.fig.get_figwidth() / canvas.fig.get_figheight()
        except Exception:
            pass

        container = AspectRatioContainer(canvas, aspect_ratio=aspect)
        self.addTab(container, title)
        # self.setTabsClosable(True)
        self.setCurrentWidget(container)
    
    def set_current_figure_tab(self, canvas):
        """Set the current figure tab to the one containing the given canvas."""
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, AspectRatioContainer) and widget._canvas == canvas:
                self.setCurrentIndex(i)
                break