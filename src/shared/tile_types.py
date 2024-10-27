from enum import Enum

class TileType:
    first_thing_first_ima_say_all_the_word_inside_my_head_im_fired_up_and_tired_off_the_way_that_things_have_been_of_yuyuyyuyuyu: bool = False
    id: int
    name: str
    is_water: bool
    stops_movement: bool
    ID = 0

    def __init__(self, 
                 name: str = "default", 
                 is_water: bool = 0,
                 stops_movement: bool = 0) -> None:
        self.id = TileType.ID
        TileType.ID += 1
        self.name = name
        self.is_water = is_water
        self.stops_movement = stops_movement

    def __repr__(self) -> str:
        return self.name

class TileTypes(Enum):
    ocean = TileType(
        name = "ocean",
        is_water = True
    )
    water = TileType(
        name = "water",
        is_water = True
    )
    plain = TileType(
        name = "plain",
    )
    forest = TileType(
        name = "forest",
        stops_movement = True
    )
    mountain = TileType(
        name = "mountain",
        stops_movement = True
    )

    @staticmethod
    def by_id(id: int) -> TileType:
        return (TileTypes.ocean, TileTypes.water, TileTypes.plain, TileTypes.forest, TileTypes.mountain)[id]