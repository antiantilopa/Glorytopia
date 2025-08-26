from typing import Annotated
from engine_antiantilopa import Vector2d
from netio import *


class CityData(Serializable):
    name: Annotated[str, SerializeField()]
    level: Annotated[int, SerializeField()]
    population: Annotated[int, SerializeField()]
    fullness: Annotated[int, SerializeField()]
    forge: Annotated[bool, SerializeField()]
    walls: Annotated[bool, SerializeField()]
    domain: Annotated[list[Vector2d], SerializeField()]
    is_capital: Annotated[bool, SerializeField()]
    pos: Annotated[Vector2d, SerializeField()]

    def __init__(self, 
                 pos: Vector2d, 
                 owner: int, 
                 name: str, 
                 level: int, 
                 population: int, 
                 fullness: int, 
                 forge: bool, 
                 walls: bool,
                 is_capital: bool,
                 domain: list[Vector2d],
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
