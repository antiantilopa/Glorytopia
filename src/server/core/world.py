from shared.tile import TileData
from shared.util.position import Pos
from shared.asset_types import TileType
from .random_map import pangea

from .tile import Tile

def get_by_height(number: int):
    mp = {
        0: TileType.get("ocean"),
        1: TileType.get("water"),
        2: TileType.get("plain"),
        3: TileType.get("forest"),
        4: TileType.get("mountain")
    }
    return mp[number]
    
class World:
    world: list[list[Tile]]
    cities_mask: list[list[bool]]
    unit_mask: list[list[bool]]
    size: Pos
    object: "World" = None

    def __init__(self, width: int, height: int, empty: bool = False) -> None:
        self.cities_mask = [[0] * width for _ in range(height)]
        self.unit_mask = [[0] * width for _ in range(height)]
        self.size = Pos(width, height)
        if empty:
            self.world = [[Tile(Pos(i, j), TileType.get("plain"), None) for i in range(width)] for j in range(height)]
            return
        else:
            world = pangea(width, height)
            self.world = [[Tile(Pos(i, j), get_by_height(world[j][i]), None) for i in range(width)] for j in range(height)]
        World.object = self
    
    def __new__(cls, *_):
        if cls.object is None:
            cls.object = super(World, cls).__new__(cls)
        return cls.object

    def __getitem__(self, index: int) -> list[Tile]:
        return self.world[index]
    
    def get(self, pos: Pos) -> Tile:
        return self.world[pos.inty()][pos.intx()]

    def is_in(self, pos: Pos) -> bool:
        return pos.is_in_box(Pos(0, 0), self.size - Pos(1, 1))