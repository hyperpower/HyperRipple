class DataExtractionManager:
    def __init__(self, application):
        self._application = application
        self._main_node = None
        self._main_window = None

    @property
    def main_node(self):
        return self._main_node

    @main_node.setter
    def main_node(self, node):
        self._main_node = node

    @property
    def main_window(self):
        return self._main_window

    @main_window.setter
    def main_window(self, window):
        self._main_window = window