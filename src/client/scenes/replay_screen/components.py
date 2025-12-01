from engine_antiantilopa import *
from shared import *

from shared.util.position import Pos

class PositionComponent(Component):
    def __init__(self, pos: Pos):
        super().__init__()
        self.pos = pos

class TileComponent(PositionComponent):
    tile_data: TileData
    def __init__(self, tile_data: TileData, pos: Vector2d):
        super().__init__(pos)
        self.tile_data = tile_data

class UnitComponent(PositionComponent):
    unit_data: UnitData
    def __init__(self, unit_data: UnitData, pos: Vector2d):
        super().__init__(pos)
        self.unit_data = unit_data

class CityComponent(PositionComponent):
    city_data: CityData
    def __init__(self, city_data: CityData, pos: Vector2d):
        super().__init__(pos)
        self.city_data = city_data

class TechComponent(Component):
    tech: TechNode
    def __init__(self, tech: TechNode):
        super().__init__()
        self.tech = tech