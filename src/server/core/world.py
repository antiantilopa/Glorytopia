from shared.tile import TileData
from shared.util.position import Pos
from shared.asset_types import TileType
from .random_map import pangea

from . import city
from . import unit
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
    city_mask: list[list["city.City|None"]]
    unit_mask: list[list["unit.Unit|None"]]
    size: Pos
    object: "World|None" = None

    def __init__(self, width: int, height: int, empty: bool = False) -> None:
        self.city_mask = [[None] * width for _ in range(height)]
        self.unit_mask = [[None] * width for _ in range(height)]
        self.size = Pos(width, height)
        if empty:
            self.world = [[None for i in range(width)] for j in range(height)]
            return
        else:
            world = pangea(width, height)
            self.world = [[Tile(Pos(i, j), get_by_height(world[j][i]), None) for i in range(width)] for j in range(height)]
        World.object = self
    
    def __new__(cls, *_, **__) -> "World":
        if cls.object is None:
            cls.object = super(World, cls).__new__(cls)
        return cls.object

    def __getitem__(self, index: int) -> list[Tile]:
        return self.world[index]
    
    def get(self, pos: Pos) -> Tile:
        if not isinstance(pos, Pos):
            pos = Pos(pos)
        if pos.y < 0 or pos.y >= self.size.y or pos.x < 0 or pos.x >= self.size.x:
            return None
        return self.world[pos.inty()][pos.intx()]
    
    def get_unit(self, pos: Pos) -> "unit.Unit":
        if not isinstance(pos, Pos):
            pos = Pos(pos)
        if pos.y < 0 or pos.y >= self.size.y or pos.x < 0 or pos.x >= self.size.x:
            return None
        return self.unit_mask[pos.inty()][pos.intx()]
    
    def get_city(self, pos: Pos) -> "city.City":
        if not isinstance(pos, Pos):
            pos = Pos(pos)
        if pos.y < 0 or pos.y >= self.size.y or pos.x < 0 or pos.x >= self.size.x:
            return None
        return self.city_mask[pos.inty()][pos.intx()]

    def is_in(self, pos: Pos) -> bool:
        return pos.is_in_box(Pos(0, 0), self.size - Pos(1, 1))
    
    def update(self, tiles: list[Tile]):
        for tile in tiles:
            self.world[tile.pos.inty()][tile.pos.intx()] = tile