class TreeNodeBase:
    def __init__(self, name="", parent=None):
        self.name = name
        self.status = None
        self.type   = None
        self.editable = True

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

    def is_editable(self):
        return self.editable
    
    def set_editable(self, editable):
        self.editable = editable
    
    def to_dict(self, include_children=True):
        data = {
            "name": self.name,
            "status": self.status,
            "type": self.type,
            "editable": self.editable,
        }
        if hasattr(self, "value"):
            data["value"] = self.value
        if include_children:
            data["children"] = [child.to_dict(include_children=True) for child in self.children]
        return data

    @classmethod
    def from_dict(cls, data, parent=None):
        node_type = data.get("type", "group")
        name = data.get("name", "")
        editable = data.get("editable", True)
        status = data.get("status", None)

        if node_type == "string":
            node = TreeNodeString(name, data.get("value", ""), parent)
        elif node_type == "number":
            node = TreeNodeNumber(name, data.get("value", 0), parent)
        else:
            node = TreeNodeGroup(name, parent)

        node.editable = editable
        node.status = status

        for child_data in data.get("children", []):
            TreeNodeBase.from_dict(child_data, node)

        return node


class TreeNodeString(TreeNodeBase):
    def __init__(self, name="", value="", parent=None):
        super().__init__(name, parent)
        self.value = value
        self.type = 'string'
    
    def type(self):
        return self.type
    
    def to_dict(self, include_children=True):
        return super().to_dict(include_children)

class TreeNodeNumber(TreeNodeBase):
    def __init__(self, name="", value=0, parent=None):
        super().__init__(name, parent)
        self.value = value
        self.type = 'number'
    
    def type(self):
        return self.type

    def to_dict(self, include_children=True):
        return super().to_dict(include_children)

class TreeNodeGroup(TreeNodeBase):
    def __init__(self, name="", parent=None):
        super().__init__(name, parent)
        self.type = 'group'
    
    def type(self):
        return self.type

    def to_dict(self, include_children=True):
        return super().to_dict(include_children)