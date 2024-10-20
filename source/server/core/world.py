from shared.vmath import Vector2d
from tile import Tile
from shared.tile_types import TileTypes
from .random_map import pangea


class World:
    world: list[list[Tile]]
    size: Vector2d
    
    object: "World" = None

    def __init__(self, width: int, heigh: int) -> None:
        world = pangea(width, heigh)
        self.size = Vector2d(width, heigh)
        self.world = [[Tile(Vector2d(i, j), TileTypes.by_id(world[j][i] // 2), world[j][i] % 2) for i in range(width)] for j in range(heigh)]
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(World, cls).__new__(cls)
        return cls.instance

    def __getitem__(self, index: int):
        return self.world[index]
    
    def get(self, pos: Vector2d) -> Tile:
        return self.world[pos.y][pos.x]

    def isIn(self, pos: Vector2d) -> bool:
        return pos.isInBox(Vector2d(0, 0), self.size - Vector2d(1, 1))