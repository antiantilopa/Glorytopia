from typing import TypeVar, Self
from ..serialization.serializer import Serializable

class GenericType(Serializable):
    types: dict[str, Self] = {}
    name: str
    id: int

    @classmethod
    def values(cls) -> list[Self]:
        return list(cls.types.values())
    
    @classmethod
    def add(cls, t: Self):
        cls.types[t.name] = t
        setattr(cls, t.name, t)
        
    @classmethod
    def get(cls, name: str) -> Self:
        return cls.types[name]
    
    @classmethod
    def by_id(cls, id: int) -> Self:
        for ttype in list(cls.types.values()):
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