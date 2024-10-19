from shared.vmath import Vector2d
from random_map import pangea
from source.shared.tile_types import TileType, TileTypes

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
    size: Vector2d

    def __init__(self, width: int, heigh: int) -> None:
        world = pangea(width, heigh)
        self.size = Vector2d(width, heigh)
        self.world = [[Tile(Vector2d(i, j), TileTypes.by_id(world[j][i] // 2), world[j][i] % 2) for i in range(width)] for j in range(heigh)]
    
    def __getitem__(self, index: int):
        return self.world[index]
    
    def get(self, pos: Vector2d):
        return self.world[pos.y][pos.x]

    def isIn(self, pos: Vector2d):
        return pos.isInBox(Vector2d(0, 0), self.size - Vector2d(1, 1))