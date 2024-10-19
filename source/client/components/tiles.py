from pygame_tools_tafh import Component, Vector2d

from .generic import SpriteComponent


class Tile:
    pass


class TileComponent(Component):

    position: Vector2d

    def __init__(self, tile: Tile, posititon: Vector2d) -> None:
        super().__init__()
        self.tile = tile
        self.position = posititon



