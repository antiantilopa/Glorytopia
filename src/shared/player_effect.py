# TODO

from netio import GenericType, Serializable
from . import unit as Unit
from . import tile as Tile

class PlayerEffect(GenericType):
    duration: int
    name: str
    
    def __init__(self, duration = -1):
        self.duration = duration

