from PySide6.QtCore import Signal, QObject
from model.node_type_registry import NodeTypeRegistry as NTR

class TreeNodeBase(QObject):
    dataChanged = Signal(object, object)
    layoutChanged = Signal(object, object, object)

    def __init__(self, name="", parent=None):
        super().__init__()

        self.name = name
        self.status = None
        self.type = 0  # 位标志
        self.editable = True
        self.value = None

        self.parent = parent 
        self.children = []

        if parent is not None:
            parent.children.append(self)
    
    def get_class_name(self):
        return self.__class__.__name__
    
    def get_ancestor_by_class_name(self, class_name : str):
        """Return a list of ancestor nodes of a specific class name."""
        if self.get_class_name() == class_name:
            return self
        else:
            current = self.parent
            while current is not None:
                if current.get_class_name() == class_name:
                    return current
                current = current.parent
        return None

    def child(self, row):
        return self.children[row] if 0 <= row < len(self.children) else None
    
    def __getitem__(self, key):
        for child in self.children:
            if child.name == key:
                return child
        raise KeyError(f"No child with name: {key}")
    
    def set_value(self, value):
        self.value = value
        self.dataChanged.emit(self, value)
    
    def __iter__(self):
        return iter(self.children)

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
        return self.type
    
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

    def get_type(self):
        """返回节点类型"""
        return self.type
    
    def has_type(self, type_name: str) -> bool:
        """判断是否包含某种类型"""
        return bool(self.type & NTR.get(type_name))
    
    def add_type(self, type_name: str):
        """添加类型"""
        self.type |= NTR.get(type_name)
    
    def remove_type(self, type_name: str):
        """移除类型"""
        self.type &= ~NTR.get(type_name)
    
    def get_type_names(self) -> list:
        """获取所有类型名称"""
        return NTR.has_names(self.type)

    def __str__(self):
        type_names = ", ".join(self.get_type_names())
        return f"TreeNode(name={self.name}, types=[{type_names}], len_children={len(self.children)})"

    def iter_by_class(self, class_name: str):
        """
        Generator: yield child nodes whose class name matches `class_name`.
        """
        for child in self.children:
            if child.__class__.__name__ == class_name:
                yield child
    
    def build_default_children(self, properties: dict = None):
        self._build_node_by_properties(self, properties)
    
    @classmethod 
    def _build_node_by_properties(cls, root_node, properties: dict):
        for key, value in properties.items():
            if isinstance(value, dict):
                node = TreeNodeGroup(key)
                cls._build_node_by_properties(node, value)
            elif isinstance(value, str):
                node = TreeNodeString(key, value)
                root_node.addChild(node)
            elif isinstance(value, (int, float)):
                node = TreeNodeNumber(key, value)
                root_node.addChild(node)
            else:
                raise ValueError(f"Unsupported property type for key '{key}': {type(value)}")
    


class TreeNodeString(TreeNodeBase):
    def __init__(self, name="", value="", parent=None):
        super().__init__(name, parent)
        # 使用字符串注册类型
        self.value = value
        self.type = NTR.get("STRING") | NTR.get("OPENABLE")

    def allowed_actions(self):
        return []


class TreeNodeNumber(TreeNodeBase):
    def __init__(self, name="", value=0, parent=None):
        super().__init__(name, parent)
        self.value = value
        self.type = NTR.get("NUMBER") | NTR.get("OPENABLE")

    def allowed_actions(self):
        return []

class TreeNodeArray(TreeNodeBase):
    def __init__(self, name="", value=None, parent=None):
        super().__init__(name, parent)
        self.value = value
        
        if self.value is None:
            self.value = []
        self.type = NTR.get("ARRAY") | NTR.get("OPENABLE")

    def allowed_actions(self):
        return []



class TreeNodeGroup(TreeNodeBase):
    def __init__(self, name="", parent=None):
        super().__init__(name, parent)
        self.type = NTR.get("GROUP") | NTR.get("EXPANDABLE")

    def allowed_actions(self):
        return ["rename", "delete"]