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
    required_resource: "ResourceType|None"
    cost: int
    population: int
    adjacent_bonus: "BuildingType|None"
    ID = 0

    def __init__(self, 
                 name :str = "default",
                 ttypes: list["TileTypes"] = [],
                 required_resource: "ResourceType|None" = None,
                 cost: int = 0,
                 population: int = 0,
                 adjacent_bonus: "BuildingType|None" = None) -> None:
        self.id = BuildingType.ID
        BuildingType.ID += 1
        self.name = name
        self.ttypes = ttypes
        self.required_resource = required_resource
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

    ID = 0

    def __init__(self, name: str = "default", ttypes: list[TileType] = []) -> None:
        self.id = ResourceType.ID
        ResourceType.ID += 1
        self.name = name
        self.ttypes = ttypes
        


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

    objs = [
        ocean,
        water,
        plain,
        forest,
        mountain
    ]

    @staticmethod
    def by_name(name: str) -> TileType:
        return TileTypes.__dict__[name]
    
    @staticmethod
    def by_id(id: int) -> TileType:
        for ttype in TileTypes.objs:
            if ttype.id == id:
                return ttype
        raise KeyError(id)
        

class ResourceTypes:
    fruits = ResourceType(
        name="fruits",
        ttypes=[TileTypes.plain]
    )
    crops = ResourceType(
        name="crops",
        ttypes=[TileTypes.plain]
    )
    fish = ResourceType(
        name="fish",
        ttypes=[TileTypes.water, TileTypes.ocean]
    )
    metal = ResourceType(
        name="metal",
        ttypes=[TileTypes.mountain]
    )
    wild_animals = ResourceType(
        name="wild_animals",
        ttypes=[TileTypes.forest]
    )

    objs = [
        fruits,
        crops,
        fish,
        metal,
        wild_animals
    ]

    @staticmethod
    def by_id(id: int) -> ResourceType:
        for rtype in ResourceTypes.objs:
            if rtype.id == id:
                return rtype
        raise KeyError(id)
    
class BuildingTypes:
    farm = BuildingType(
        name="farm",
        ttypes=[TileTypes.plain],
        required_resource=ResourceTypes.crops,
        cost=5,
        population=2
    )
    mine = BuildingType(
        name="mine",
        ttypes=[TileTypes.mountain],
        required_resource=ResourceTypes.metal,
        cost=5,
        population=2
    )

    objs = [
        farm,
        mine
    ]
    @staticmethod
    def by_id(id: int) -> BuildingType:
        for btype in BuildingTypes.objs:
            if btype.id == id:
                return btype
        raise KeyError(id)
    