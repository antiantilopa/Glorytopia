from engine_antiantilopa import Vector2d
from netio import Serializable, SerializeField
from typing import Annotated
from .asset_types import TileType, BuildingType, ResourceType

class TileData(Serializable):
    pos: Annotated[Vector2d, SerializeField()]
    ttype: Annotated[TileType, SerializeField(by_id=True)]
    resource: Annotated[ResourceType, SerializeField(by_id=True)]
    has_road: Annotated[bool, SerializeField()]
    owner: Annotated[int, SerializeField()]
    building: Annotated[BuildingType | None, SerializeField()]

    def __init__(self, pos: Vector2d, ttype: TileType, resource: ResourceType) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resource = resource
        self.building = None
        self.has_road = False
        self.owner = -1
