from .serialization.serializer import Serializable
from typing import Self

Address = tuple[str, int]

class ConnectionData(Serializable, primitive = 1):
    def __tuple__(self):
        return tuple()

class PlayerData(Serializable):

    address: Address
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        orig_create = cls.create

        def new_create(cls: type[PlayerData], *a, **kw):
            self = orig_create(cls, *a, **kw)
            self._clear_updates()
            return self

        cls.create = new_create
    
    @classmethod
    def create(cls, addr: Address, conn_data: ConnectionData) -> Self:
        obj = cls.__new__(cls)
        cls.__init__(obj)
        assert isinstance(obj, PlayerData)
        obj.address = addr
        return obj
    
    def __str__(self):
        return f"PlayerData <{self.address}>"

    def __repr__(self):
        return f"PlayerData <{self.address}>"
