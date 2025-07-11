from typing import TypeVar, Self

T = TypeVar("T")

class GenericType[T]:
    types: dict[str, T] = {}

    def __init_subclass__(cls):
        types = {}

        def values():
            return list(types.values())
        
        def add(t: T):
            types[t.name] = t
        
        def get(name: str) -> T:
            return types[name]
        
        def func(id: int):
            for ttype in list(types.values()):
                if ttype.id == id:
                    return ttype
            raise KeyError(id)
        
        cls.get = get
        cls.add = add
        cls.by_id = func
        cls.values = values

    @staticmethod
    def values() -> list[T]:
        return list(GenericType.types.values())
    
    @staticmethod
    def add(t: T):
        GenericType.types[t.name] = t
        setattr(GenericType, t.name, t)
        
    @staticmethod
    def get(name: str) -> T:
        return GenericType.types[name]
    
    @staticmethod
    def by_id(id: int) -> T:
        for ttype in list(GenericType.types.values()):
            if ttype.id == id:
                return ttype
        raise KeyError(id)
    
    def __eq__(self, value):
        if value is None:
            return False
        return self.name == value.name
    
    def __ne__(self, value):
        if value is None:
            return True
        return self.name != value.name