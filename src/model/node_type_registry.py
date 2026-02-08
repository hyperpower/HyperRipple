class NodeTypeRegistry:
    """节点类型注册表 - 支持动态注册类型"""
    
    _next_flag = 1
    _types = {}
    
    @classmethod
    def register(cls, name: str) -> int:
        """注册新类型，返回唯一标志位"""
        if name in cls._types:
            return cls._types[name]
        
        flag = cls._next_flag
        cls._types[name] = flag
        cls._next_flag <<= 1  # 左移一位，生成下一个标志
        return flag
    
    @classmethod
    def get(cls, name: str) -> int:
        """获取类型标志"""
        return cls._types.get(name, 0)
    
    @classmethod
    def get_name(cls, flag: int) -> str:
        """根据标志获取名称"""
        for name, f in cls._types.items():
            if f == flag:
                return name
        return "UNKNOWN"
    
    @classmethod
    def has_names(cls, flag: int) -> list:
        """获取flag包含的所有类型名称"""
        names = []
        for name, f in cls._types.items():
            if flag & f:
                names.append(name)
        return names
    
    @classmethod
    def all_types(cls):
        """返回所有已注册类型"""
        return cls._types.copy()


# 预注册核心类型
NodeTypeRegistry.register("NONE")       # 0
NodeTypeRegistry.register("STRING")     # 1
NodeTypeRegistry.register("NUMBER")     # 2
NodeTypeRegistry.register("BOOLEAN")    # 4
NodeTypeRegistry.register("GROUP")      # 8
NodeTypeRegistry.register("EDITABLE")   # 16
NodeTypeRegistry.register("OPENABLE")   # 32
NodeTypeRegistry.register("EXPANDABLE") # 64