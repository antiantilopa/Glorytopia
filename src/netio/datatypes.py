from .serialization.serializer import Serializable
from typing import Self

Address = tuple[str, int]

class ConnectionData(Serializable):
    pass

class PlayerData(Serializable):

    address: Address
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        orig_create = cls.create

        def new_create(self: PlayerData, *a, **kw):
            orig_create(self, *a, **kw)
            self._clear_updates()

        cls.create = new_create
    
    @classmethod
    def create(cls, addr: Address, conn_data: ConnectionData) -> Self:
        obj = cls.__new__(cls)
        assert isinstance(obj, PlayerData)
        obj.address = addr
        return obj
    
    def __str__(self):
        return f"PlayerData <{self.address}>"

    def __repr__(self):
        return f"PlayerData <{self.address}>"
