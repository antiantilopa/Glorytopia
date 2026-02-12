from shared.generic_object import GenericObject
from shared.util.position import Pos
from netio import Serializable, SerializeField
from typing import Annotated
from .asset_types import TileType, BuildingType, ResourceType
from .modificator import TileModificator

class TileData(GenericObject):
    pos: Annotated[Pos, SerializeField()]
    type: Annotated[TileType, SerializeField()]
    has_road: Annotated[bool, SerializeField()]
    owner: Annotated[int, SerializeField()]
    resource: Annotated[ResourceType|None, SerializeField()]
    building: Annotated[BuildingType|None, SerializeField()]
    modificators: Annotated[list[TileModificator], SerializeField()]

    def __init__(self, pos: Pos, tile_type: TileType, resource: ResourceType) -> None:
        self.pos = pos
        self.type = tile_type
        self.resource = resource
        self.building = None
        self.has_road = False
        self.modificators = []
        self.owner = -1

