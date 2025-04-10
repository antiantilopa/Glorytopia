from .tile import Tile
from pygame_tools_tafh import Vector2d, is_in_box
from shared.tile_types import TileTypes
from .random_map import pangea


class World:
    world: list[list[Tile]]
    cities_mask: list[list[bool]]
    unit_mask: list[list[bool]]
    size: Vector2d
    object: "World" = None

    def __init__(self, width: int, height: int) -> None:
        world = pangea(width, height)
        self.cities_mask = [[0] * width for _ in range(height)]
        self.unit_mask = [[0] * width for _ in range(height)]
        self.size = Vector2d(width, height)
        self.world = [[Tile(Vector2d(i, j), TileTypes.by_id(world[j][i]), None) for i in range(width)] for j in range(height)]
        World.object = self
    
    def __new__(cls, *_):
        if cls.object is None:
            cls.object = super(World, cls).__new__(cls)
        return cls.object

    def __getitem__(self, index: int) -> list[Tile]:
        return self.world[index]
    
    def get(self, pos: Vector2d) -> Tile:
        return self.world[pos.inty()][pos.intx()]

    def is_in(self, pos: Vector2d) -> bool:
        return is_in_box(pos, Vector2d(0, 0), self.size - Vector2d(1, 1))
