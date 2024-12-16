import pygame, os
from pygame_tools_tafh import Component, Vector2d, camera
from pygame import Surface
from typing import Callable

DEBUG = True

class LabelComponent(Component):

    def __init__(self, text: str, color: tuple[int, int, int]):
        p = "\\".join(os.path.dirname(__file__).split("\\")[0:-1])
        p = os.path.join(p, "assets", "Beyond Wonderland.ttf")
        self.font = pygame.font.Font(p, 50)
        self.text = text
        self.scale_x = 1
        self.scale_y = 1
        self.color = color
        
    def draw(self, display: pygame.Surface):
        sum_height = 0
        for i in self.text.split("\n"):
            # TODO: Rework it so center of whole passage will be at right center.
            text = self.font.render(i, True, self.color)

            text = pygame.transform.scale(text, (text.get_width() * self.scale_x, text.get_height() * self.scale_y))
            display.blit(text, text.get_rect(center=
                (self.game_object.transform.position + Vector2d(0, sum_height)).as_tuple()))
            sum_height += text.get_height()


class ButtonComponent(Component):

    def __init__(self, cmd: Callable, interception: Callable[[Vector2d, Vector2d], bool], *args):
        self.cmd = cmd
        self.interception = interception
        self.args = args

    def update(self):
        if pygame.mouse.get_pressed(3)[0]:
            pos = Vector2d.from_tuple(pygame.mouse.get_pos())
            if self.interception(camera.normalize(self.game_object.transform.position), pos):
                self.cmd(self.args)


class RectButtonComponent(ButtonComponent):

    def __init__(self, cmd: Callable, size: Vector2d, *args):
        self.size = size
        def interception(center: Vector2d, position: Vector2d) -> bool:
            temp = (center - position).operation(size, lambda a, b: -b/2 <= a <= b/2)
            return bool(temp.x) and bool(temp.y)

        super().__init__(cmd, interception)

    def draw(self, display: pygame.Surface):
        if DEBUG:
            top_left = (self.game_object.transform.position - self.size / 2)
            pygame.draw.rect(display, (200, 200, 200), (top_left.x, top_left.y, self.size.x, self.size.y), width=1)

class CircleButtonComponent(ButtonComponent):

    def __init__(self, cmd: Callable, radius: float, *args):
        self.radius = radius
        def interception(center: Vector2d, position: Vector2d) -> bool:
            return (center - position).norm() <= radius

        super().__init__(cmd, interception)

class SpriteComponent(Component):
    path: str = ''
    loaded: dict = {}

    def __init__(self, sprite_name: str, size: tuple[int, int]) -> None:
        super().__init__()

        if sprite_name in SpriteComponent.loaded.keys():
            self.texture = SpriteComponent.loaded[sprite_name]
        else:
            self.texture = pygame.image.load(os.path.join(SpriteComponent.path, sprite_name)).convert_alpha()
            SpriteComponent.loaded[sprite_name] = self.texture

        self.size = size
        self.opacity = 255

    @staticmethod
    def set_path(path: str):
        SpriteComponent.path = path

    def draw(self, display: Surface):
        self.texture.set_alpha(self.opacity)
        blitImage = self.texture

        cropped = pygame.Surface(self.size)
        cropped.blit(blitImage, (0, 0))

        angle = self.game_object.transform.angle.get()
        scale = self.game_object.transform.scale

        if angle != 0:
            cropped = pygame.transform.rotate(cropped, angle)

        if scale != 1:
            cropped = pygame.transform.scale_by(cropped, scale)

        rect = cropped.get_rect(center=self.game_object.transform.position.as_tuple())

        if DEBUG:
            pygame.draw.rect(display, (255, 0, 0), rect, 1)
        display.blit(blitImage, rect)

