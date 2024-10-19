from shared.vmath import Vector2d
from random_map import pangea
from tile_types import TileType, TileTypes
class Tile:
    pos: Vector2d
    ttype: TileType
    resources: bool
    hasroad: bool
    building: ... #Building

    def __init__(self, pos: Vector2d, ttype: TileType, resources: bool) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resources = resources
        self.building = None
        self.hasroad = False
    
    def buildBuilding(self, building):
        self.building = building
        
class BuildingTypes:
    id: int
    name: str
    terrain: TileType
    cost: int


class World:
    world: list[list[Tile]]
    def __init__(self, width: int, heigh: int) -> None:
        world = pangea(width, heigh)
        self.world = [[Tile(Vector2d(i, j), TileTypes.by_id(world[j][i] // 2), world[j][i] % 2) for i in range(width)] for j in range(heigh)]