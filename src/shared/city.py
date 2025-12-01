from typing import Annotated
from shared.util.position import Pos
from netio import *


class CityData(Serializable):
    pos: Annotated[Pos, SerializeField()]
    owner: Annotated[int, SerializeField()]
    name: Annotated[str, SerializeField()]
    level: Annotated[int, SerializeField()]
    population: Annotated[int, SerializeField()]
    fullness: Annotated[int, SerializeField()]
    forge: Annotated[bool, SerializeField()]
    walls: Annotated[bool, SerializeField()]
    is_capital: Annotated[bool, SerializeField()]
    domain: Annotated[list[Pos], SerializeField()]

    def __init__(self, 
                 pos: Pos, 
                 owner: int, 
                 name: str, 
                 level: int, 
                 population: int, 
                 fullness: int, 
                 forge: bool, 
                 walls: bool,
                 is_capital: bool,
                 domain: list[Pos],
                 ):
        self.pos = pos
        self.owner = owner
        self.name = name
        self.level = level
        self.population = population
        self.fullness = fullness
        self.forge = forge
        self.walls = walls
        self.is_capital = is_capital
        self.domain = domain
