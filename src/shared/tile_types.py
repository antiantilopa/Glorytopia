class TileType:
    first_thing_first_ima_say_all_the_word_inside_my_head_im_fired_up_and_tired_off_the_way_that_things_have_been_of_yuyuyyuyuyu: bool = False
    id: int
    name: str
    is_water: bool
    stops_movement: bool

    ID = 0
    ttypes: list["TileType"] = []
    def __init__(self, 
                 name: str = "default", 
                 is_water: bool = 0,
                 stops_movement: bool = 0) -> None:
        self.id = TileType.ID
        TileType.ID += 1
        self.name = name
        self.is_water = is_water
        self.stops_movement = stops_movement
        TileType.ttypes.append(self)

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
    btypes: list["BuildingType"] = []
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
        BuildingType.btypes.append(self)
    
    def __repr__(self) -> str:
        return self.name

class ResourceType:
    id: int
    name: str
    ttypes: list[TileType]

    ID = 0
    rtypes: list["ResourceType"] = []

    def __init__(self, name: str = "default", ttypes: list[TileType] = []) -> None:
        self.id = ResourceType.ID
        ResourceType.ID += 1
        self.name = name
        self.ttypes = ttypes
        ResourceType.rtypes.append(self)


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
    
    @staticmethod
    def by_id(id: int) -> TileType:
        for ttype in TileType.ttypes:
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

    @staticmethod
    def by_id(id: int) -> ResourceType:
        for rtype in ResourceType.rtypes:
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
    windmill = BuildingType(
        name="windmill",
        ttypes=[TileTypes.plain],
        adjacent_bonus=farm,
        cost=5,
        population=1
    )
    mine = BuildingType(
        name="mine",
        ttypes=[TileTypes.mountain],
        required_resource=ResourceTypes.metal,
        cost=5,
        population=2
    )
    forge = BuildingType(
        name="forge",
        ttypes=[TileTypes.plain],
        adjacent_bonus=mine,
        cost=5,
        population=2
    )
    hut = BuildingType(
        name="hut",
        ttypes=[TileTypes.forest],
        cost=3,
        population=1
    )
    sawmill = BuildingType(
        name="sawmill",
        ttypes=[TileTypes.plain],
        adjacent_bonus=hut,
        cost=5,
        population=1
    )
    port = BuildingType(
        name="port",
        ttypes=[TileTypes.water],
        cost=7,
        population=1
    )
    market = BuildingType(
        name="market",
        ttypes=[TileTypes.plain],
        adjacent_bonus=port, # Not port! TODO
        cost=5,
        population=1
    )

    @staticmethod
    def by_id(id: int) -> BuildingType:
        for btype in BuildingType.btypes:
            if btype.id == id:
                return btype
        raise KeyError(id)
    