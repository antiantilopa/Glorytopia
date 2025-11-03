from shared.util.position import Pos
from netio import Serializable, SerializeField
from typing import Annotated
from .asset_types import TileType, BuildingType, ResourceType

class TileData(Serializable):
    pos: Annotated[Pos, SerializeField()]
    ttype: Annotated[TileType, SerializeField(by_id=True)]
    resource: Annotated[ResourceType, SerializeField(by_id=True)]
    has_road: Annotated[bool, SerializeField()]
    owner: Annotated[int, SerializeField()]
    building: Annotated[BuildingType | None, SerializeField()]

    def __init__(self, pos: Pos, ttype: TileType, resource: ResourceType) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resource = resource
        self.building = None
        self.has_road = False
        self.owner = -1
