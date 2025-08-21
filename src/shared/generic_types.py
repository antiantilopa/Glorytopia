from typing import TypeVar, Self

from shared.io.serializable import Serializable

T = TypeVar("T")

class GenericType[T](Serializable):
    types: dict[str, T] = {}
    name: str
    id: int

    def __init_subclass__(cls, use_from_serializable: bool = True):
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
        
        def from_serializable(id):
            return cls.by_id(id)

        cls.get = get
        cls.add = add
        cls.by_id = func
        cls.values = values

        if use_from_serializable:
            cls.from_serializable = from_serializable

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
    
    def to_serializable(self):
        return self.id
    
    @staticmethod
    def from_serializable(id):
        return GenericType.by_id(id)

    def __eq__(self, value):
        if value is None:
            return False
        return self.name == value.name
    
    def __ne__(self, value):
        if value is None:
            return True
        return self.name != value.name