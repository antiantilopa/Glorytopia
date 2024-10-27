from pygame_tools_tafh import Component, Vector2d
from shared.tile import TileData


class TileComponent(Component):

    position: Vector2d

    def __init__(self, tile: TileData, position: Vector2d) -> None:
        super().__init__()
        self.tile = tile
        self.position = position



