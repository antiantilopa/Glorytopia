from vmath import Vector2d

from .tile_types import TileType


class TileData:
    pos: Vector2d
    ttype: TileType
    resources: bool
    has_road: bool
    owner: int
    building: ... #Building

    def __init__(self, pos: Vector2d, ttype: TileType, resources: bool) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resources = resources
        self.building = None
        self.has_road = False
        self.owner = -1