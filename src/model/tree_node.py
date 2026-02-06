


class TreeNodeBase:
    def __init__(self, name="", parent=None):
        self.name = name
        self.status = None
        self.type   = None

        self.parent = parent 
        self.children = []

        if parent is not None:
            parent.children.append(self)

    def child(self, row):
        return self.children[row] if 0 <= row < len(self.children) else None

    def childCount(self):
        return len(self.children)
    
    def is_leaf(self):
        return len(self.children) == 0

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def addChild(self, item):
        item.parent = self
        self.children.append(item)

    def removeChild(self, row):
        if 0 <= row < len(self.children):
            self.children.pop(row)
    
    def type(self):
        return "base"


class TreeNodeString(TreeNodeBase):
    def __init__(self, name="", value="", parent=None):
        super().__init__(name, parent)
        self.value = value
        self.type = 'string'
    
    def type(self):
        return self.type

class TreeNodeNumber(TreeNodeBase):
    def __init__(self, name="", value=0, parent=None):
        super().__init__(name, parent)
        self.value = value
        self.type = 'number'
    
    def type(self):
        return self.type

class TreeNodeGroup(TreeNodeBase):
    def __init__(self, name="", parent=None):
        super().__init__(name, parent)
        self.type = 'group'
    
    def type(self):
        return self.type
    