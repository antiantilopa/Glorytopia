from pygame_tools_tafh import Vector2d


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