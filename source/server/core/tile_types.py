from enum import Enum

class TileType:
    first_thing_first_ima_say_all_the_word_inside_my_head_im_fired_up_and_tired_off_the_way_that_things_have_been_of_yuyuyyuyuyu: bool = False
    id: int
    name: str
    iswater: bool
    stopsmovement: bool
    ID = 0

    def __init__(self, 
                 name: str = "default", 
                 iswater: bool = 0, 
                 stopsmovement: bool = 0) -> None:
        self.id = TileType.ID
        TileType.ID += 1
        self.name = name
        self.iswater = iswater
        self.stopsmovement = stopsmovement

    def __repr__(self) -> str:
        return self.name

class TileTypes(Enum):
    ocean = TileType(
        name = "ocean",
        iswater = 1
    )
    water = TileType(
        name = "water",
        iswater = 1
    )
    plain = TileType(
        name = "plain",
    )
    forest = TileType(
        name = "forest",
        stopsmovement = 1
    )
    mountain = TileType(
        name = "mountain",
        stopsmovement = 1
    )
    def by_id(id: int) -> TileType:
        return (TileTypes.ocean, TileTypes.water, TileTypes.plain, TileTypes.forest, TileTypes.mountain)[id]