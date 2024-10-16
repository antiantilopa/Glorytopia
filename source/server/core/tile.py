from ..vmath import *

class TileType:
    first_thing_first_ima_say_all_the_word_inside_my_head_im_fired_up_and_tired_off_the_way_that_things_have_been_of_yuyuyyuyuyu: bool = False
    id: int
    name: str
    iswater: bool
    stopsmovement: bool
    ID = 0

    def __init__(self, name: str, iswater: bool, stopsmovement: bool) -> None:
        self.id = TileType.ID
        TileType.ID += 1
        self.name = name
        self.iswater = iswater
        self.stopsmovement = stopsmovement

    def __repr__(self) -> str:
        return self.name

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
    def __init__(self) -> None:
        pass