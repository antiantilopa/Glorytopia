from pygame_tools_tafh import *
from shared.tile import TileData
from shared.tile_types import TileTypes

tile_size = 120


class TileComponent(SpriteComponent, TileData):

    def __init__(self, tile_data: TileData):
        path = {
            TileTypes.plain: "tile.png",
            # TileTypes.water: "water.png",
            # TileTypes.mountain: "mountain.png",
            # TileTypes.ocean: "road.png",
            # TileTypes.forest: "forest.png",
            # TileTypes.popa: "popa.png",
        }[tile_data.ttype]

        SpriteComponent.__init__(self, path, (tile_size, tile_size))
        self.__dict__.update(tile_data.__dict__)
        self.game_object.transform.position = self.pos * tile_size

class NotFuckingImplemented(NotImplemented): pass

class WorldComponent(Component):

    def __init__(self, world: list[list[TileData]], size: Vector2d):
        raise NotFuckingImplemented
