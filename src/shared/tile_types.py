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

class BuildingType:
    id: int
    name: str
    ttypes: list[TileType]
    prev: "BuildingType"
    cost: int
    population: int
    adjacent_bonus: "BuildingType|None"
    ID = 0

    def __init__(self, 
                 name :str = "default",
                 ttypes: list["TileTypes"] = [],
                 prev: "BuildingType|None" = None,
                 cost: int = 0,
                 population: int = 0,
                 adjacent_bonus: "BuildingType|None" = None) -> None:
        self.id = BuildingType.ID
        BuildingType.ID += 1
        self.name = name
        self.ttypes = ttypes
        self.prev = prev
        self.cost = cost
        self.population = population
        self.adjacent_bonus = adjacent_bonus
    
    def __repr__(self) -> str:
        return self.name

class Building:
    level: int
    btype: BuildingType

    def __init__(self, btype: BuildingType) -> None:
        self.btype = BuildingType

class ResourceType:
    id: int
    name: str
    ttypes: list[TileType]


class TileTypes:
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
    def by_name(name: str) -> TileType:
        return TileTypes.__dict__[name]
        

class BuildingTypes:
    destroy = BuildingType(
        name="destroy",
        ttypes=[],
        cost=5,
        population=0
    )
    gold = BuildingType(
        name="gold",
        ttypes=[TileTypes.mountain],
        cost=0,
        population=0
    )
    mine = BuildingType(
        name="mine",
        ttypes=[TileTypes.mountain],
        prev=gold,
        cost=5,
        population=2
    )


    @staticmethod
    def by_id(id: int) -> BuildingType:
        return NotImplemented
    
