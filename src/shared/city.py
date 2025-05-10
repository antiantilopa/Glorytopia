from pygame_tools_tafh import Vector2d
from serializator.net import flags_to_int, int_to_flags

SerializedCity = tuple[str, int, tuple[int, int], int, int, int, list[tuple[int, int]], int]

class CityData:
    name: str
    level: int
    population: int
    fullness: int
    forge: bool
    walls: bool
    domain: list[Vector2d]
    pos: Vector2d

    def __init__(self, 
                 pos: Vector2d, 
                 owner: int, 
                 name: str, 
                 level: int, 
                 population: int, 
                 fullness: int, 
                 forge: bool, 
                 walls: bool,
                 domain: list[Vector2d]):
        self.pos = pos
        self.owner = owner
        self.name = name
        self.level = level
        self.population = population
        self.fullness = fullness
        self.forge = forge
        self.walls = walls
        self.domain = domain
    
    def to_serializable(self):
        return [self.name, self.owner, self.pos.as_tuple(), self.level, self.population, self.fullness, [pos.as_tuple() for pos in self.domain], flags_to_int(self.forge, self.walls)]
    
    def from_serializable(serializable: SerializedCity) -> "CityData":
        cdata = CityData(Vector2d.from_tuple(serializable[2]), serializable[1], serializable[0], serializable[3], serializable[4], serializable[5], False, False, [])
        cdata.forge, cdata.walls = int_to_flags(serializable[7], 2)
        cdata.domain = [Vector2d.from_tuple(pos) for pos in serializable[6]]
        return cdata