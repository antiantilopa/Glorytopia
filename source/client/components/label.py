import pygame
from pygame_tools_tafh import Component, Vector2d


class LabelComponent(Component):

    def __init__(self, text: str, color: tuple[int, int, int]):
        self.font = pygame.font.Font("source/client/assets/Beyond Wonderland.ttf", 50)
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