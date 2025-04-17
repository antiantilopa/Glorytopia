from pygame_tools_tafh.vmath import Vector2d

from .tile_types import TileType, BuildingType, ResourceType


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