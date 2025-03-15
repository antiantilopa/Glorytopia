from pygame_tools_tafh import GameObject, SpriteComponent, Vector2d, Transform
from shared.tile import TileData


class TileComponent(SpriteComponent):

    position: Vector2d

    def __init__(self, tile: TileData, position: Vector2d) -> None:
        super().__init__()
        self.tile = tile
        self.position = position
    
    def place(self) -> None:
        if not self.game_object is None:
            if not self.game_object.get_component(Transform) is None:
                self.game_object.get_component(Transform).position = self.position


