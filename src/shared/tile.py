from engine_antiantilopa import Vector2d

from .asset_types import TileType, BuildingType, ResourceType

SerializedTile = tuple[int, int, tuple[int, int], int, int, bool]

class TileData:
    pos: Vector2d
    ttype: TileType
    resource: ResourceType
    has_road: bool
    owner: int
    building: BuildingType|None

    def __init__(self, pos: Vector2d, ttype: TileType, resource: ResourceType) -> None:
        self.pos = pos
        self.ttype = ttype
        self.resource = resource
        self.building = None
        self.has_road = False
        self.owner = -1

    def to_serializable(self):
        if self.resource is None:
            resource_id = -1
        else:
            resource_id = self.resource.id
        if self.building is None:
            building_id = -1
        else:
            building_id = self.building.id
        return [self.ttype.id, self.owner, self.pos.as_tuple(), resource_id, building_id, self.has_road]

    @staticmethod
    def from_serializable(serializable: SerializedTile) -> "TileData":
        tdata = TileData(
            Vector2d.from_tuple(serializable[2]), 
            TileType.by_id(serializable[0]), 
            ResourceType.by_id(serializable[3]) if serializable[3] >= 0 else None
        )
        tdata.owner = serializable[1]
        tdata.building = BuildingType.by_id(serializable[4]) if serializable[4] >= 0 else None
        tdata.has_road = serializable[5]
        return tdata