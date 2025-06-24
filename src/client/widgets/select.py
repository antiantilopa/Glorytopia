from engine_antiantilopa import *
import pygame as pg

class SelectComponent(Component):
    is_selected: bool

    selected: GameObject|None = None

    def __init__(self):
        super().__init__()
        self.is_selected = False

    def select(self):
        self.is_selected = True
        if SelectComponent.selected is not None:
            SelectComponent.selected.get_component(SelectComponent).is_selected = False
        SelectComponent.selected = self.game_object

    def deselect(self):
        self.is_selected = False
        SelectComponent.selected = None
    
    def destroy(self):
        if SelectComponent.selected == self.game_object:
            self.deselect()
        return super().destroy()