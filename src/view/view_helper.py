

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPalette, QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer

def createThemedPixmap(svg_path, size=24, color=None):
    """创建适配主题的图标"""
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
            
        # 获取当前文本颜色
        if color is None:
            color = QApplication.palette().color(QPalette.WindowText).name()
        # 替换 currentColor
        svg_content = svg_content.replace('currentColor', color)
            
        # 渲染 SVG
        renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
    except Exception as e:
        print(f"Failed to load icon {svg_path}: {e}")
        return QPixmap()


def createThemedIcon(svg_path, size=24, color=None):
    """创建适配主题的图标"""
    pixmap = createThemedPixmap(svg_path, size, color)
    return QIcon(pixmap)