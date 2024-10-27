import pygame, os
from pygame_tools_tafh import Component, Vector2d
from typing import Callable

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
        cnt = 0
        for i in self.text.split("\n"):
            text = self.font.render(i, True, self.color)

            text = pygame.transform.scale(text, (text.get_width() * self.scale_x, text.get_height() * self.scale_y))
            display.blit(text, text.get_rect(center=
                                             (self.game_object.transform.position + Vector2d(0, 50 * cnt)).as_tuple()))
            cnt += 1

class ButtonComponent(Component):

    def __init__(self, cmd: Callable, interception: Callable[[Vector2d, Vector2d], bool], *args):
        self.cmd = cmd
        self.interception = interception
        self.args = args

    def update(self):
        if pygame.mouse.get_pressed(3)[0]:
            pos = Vector2d.from_tuple(pygame.mouse.get_pos())
            if self.interception(self.game_object.transform.position, pos):
                self.cmd(self.args)


