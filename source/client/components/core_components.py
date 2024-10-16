import pygame_tools_tafh as pgt

from pygame_tools_tafh import GameObject, Component

class UnitComponent(Component):

    def __init__(self):
        super().__init__()
        
    def draw(self, screen):
        super().draw(screen)
        