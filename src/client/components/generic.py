import pygame_tools_tafh as pgt
import pygame
from pygame_tools_tafh import GameObject, Component, Vector2d
from shared.unit import UnitData


class SpriteComponent(Component):

    def __init__(self, path: str, width: int, height: int) -> None:
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.scale = 1
        self.angle = 0

    def draw(self, display: pgt.Surface):
        image = pygame.transform.rotate(self.image, self.angle)
        image = pygame.transform.scale_by(image, self.scale)

        center = self.game_object.transform.position.as_tuple()
        display.blit(image, image.get_rect(center=center))
        return super().draw(display)


class UnitComponent(Component, UnitData):

    health: int
    position: Vector2d

    def __init__(self):
        super().__init__()
        