class UpdatingObject:
    objs: list["UpdatingObject"] = []
    updated_objs: list["UpdatingObject"] = []
    black_list: list[str]
    sub_clss: list[type["UpdatingObject"]] = []

    def __init__(self):
        UpdatingObject.objs.append(self)
        self.black_list = ["objs", "updated_objs", "black_list, updated"]
        self.updated = False

    def __init_subclass__(cls):
        UpdatingObject.sub_clss.append(cls)
        UpdatingObject.sub_clss.sort(key=lambda x: x.__name__)

    def __setattr__(self, name, value):
        if name in ("objs", "updated_objs", "black_list", "updated"):
            return object.__setattr__(self, name, value)
        elif name in self.black_list:
            return object.__setattr__(self, name, value)
        if not self.updated:
            if hasattr(self, name):
                if object.__getattribute__(self, name) == value:
                    return 
            UpdatingObject.updated_objs.append(self)
            object.__setattr__(self, "updated", True)
        object.__setattr__(self, name, value)
    
    def refresh_updated(self):
        if self.updated:
            self.updated = False
            UpdatingObject.updated_objs.remove(self)

    def destroy(self):
        if self in UpdatingObject.objs:
            UpdatingObject.objs.remove(self)
        if self in UpdatingObject.updated_objs:
            UpdatingObject.updated_objs.remove(self)
    
    def set_from_data(self, data):
        raise NotImplementedError()

    def to_serializable(self):
        raise NotImplementedError()
    
    @staticmethod
    def from_serializable(data):
        raise NotImplementedError()
        
    @staticmethod
    def do_serializable(data):
        raise NotImplementedError()
