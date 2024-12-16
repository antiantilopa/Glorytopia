import pygame_tools_tafh as pgt
import pygame
from pygame_tools_tafh import GameObject, Component, Vector2d
from shared.unit import UnitData

class UnitComponent(Component, UnitData):

    health: int
    position: Vector2d

    def __init__(self):
        super().__init__()
        