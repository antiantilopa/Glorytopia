from shared.generic_types import GenericType
from . import unit as Unit
from . import tile as Tile

class PlayerEffect(GenericType["PlayerEffect"]):
    id = -1
    duration: int
    name: str

    ID = 0

    def __init_subclass__(cls):
        PlayerEffect.add(cls)
        cls.id = PlayerEffect.ID
        PlayerEffect.ID += 1
    
    def __init__(self, duration = -1):
        self.duration = duration

