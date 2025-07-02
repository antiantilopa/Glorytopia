class UpdatingObject:
    objs: list["UpdatingObject"] = []
    updated_objs: list["UpdatingObject"] = []

    def __init__(self):
        UpdatingObject.objs.append(self)
        self.updated = False

    def __setattr__(self, name, value):
        if name == "updated":
            return object.__setattr__(self, name, value)
        if not self.updated:
            if hasattr(self, name):
                if object.__getattribute__(self, name) == value:
                    return 
                print(f"UpdatingObject: {self.__class__.__name__} {name} = {value}")
            else:
                print(f"UpdatingObject: {self.__class__.__name__} {name} := {value}")
            UpdatingObject.updated_objs.append(self)
            object.__setattr__(self, "updated", True)
        object.__setattr__(self, name, value)
    
    def refresh_updated(self):
        if self.updated:
            print(f"updated: {self.__class__.__name__}")
            self.updated = False
            UpdatingObject.updated_objs.remove(self)

    def destroy(self):
        if self in UpdatingObject.objs:
            UpdatingObject.objs.remove(self)
        if self in UpdatingObject.updated_objs:
            UpdatingObject.updated_objs.remove(self)