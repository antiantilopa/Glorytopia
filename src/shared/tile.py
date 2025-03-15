from pygame_tools_tafh.vmath import Vector2d

from .tile_types import TileType, BuildingType, ResourceType


class TileData:
    pos: Vector2d
    ttype: TileType
    resource: ResourceType
    has_road: bool
    owner: int
    building: BuildingType|None

    def __init__(self, pos: Vector2d, ttype: TileType, resource: ResourceType) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resource = resource
        self.building = None
        self.has_road = False
        self.owner = -1