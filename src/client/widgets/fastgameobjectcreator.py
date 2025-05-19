from engine_antiantilopa import *
from ..widgets.shapes import RectBorderShapeComponent
from enum import Enum
import pygame as pg

class Position(Enum):
    CENTER = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3
    UP = 4
    LEFT_DOWN = 5
    RIGHT_DOWN = 6
    RIGHT_UP = 7
    LEFT_UP = 8

    funcs = [
        lambda v1, v2: Vector2d(0, 0),
        lambda v1, v2: Vector2d(v1.x - v2.x, 0) // 2,
        lambda v1, v2: Vector2d(0, v2.y - v1.y) // 2,
        lambda v1, v2: Vector2d(v2.x - v1.x, 0) // 2,
        lambda v1, v2: Vector2d(0, v1.y - v2.y) // 2,
        lambda v1, v2: Vector2d(v1.x - v2.x, v2.y - v1.y) // 2,
        lambda v1, v2: Vector2d(v2.x - v1.x, v2.y - v1.y) // 2,
        lambda v1, v2: Vector2d(v2.x - v1.x, v1.y - v2.y) // 2,
        lambda v1, v2: Vector2d(v1.x - v2.x, v1.y - v2.y) // 2
    ]

    @staticmethod
    def get_vector_pos(pos: "Position", v1, v2) -> Vector2d:
        return Position.funcs.value[pos.value](v1, v2)
    
class Shape(Enum):
    RECT = RectShapeComponent
    CIRCLE = CircleShapeComponent
    RECTBORDER = RectBorderShapeComponent

class InGrid:
    grid: Vector2d
    pos: Vector2d

    def __init__(self, grid: Vector2d|tuple[int, int], pos: Vector2d|tuple[int, int]):
        if isinstance(grid, Vector2d):
            self.grid = grid
        else:
            self.grid = Vector2d.from_tuple(grid)
        if isinstance(pos, Vector2d):
            self.pos = pos
        else:
            self.pos = Vector2d.from_tuple(pos)

    def get_pos(self, game_object: GameObject) -> Vector2d:
        c = game_object.parent.get_component(SurfaceComponent).size
        l = Vector2d(c.x // self.grid.x, c.y // self.grid.y) // 2
        r = Vector2d(c.x // self.grid.x, 0)
        d = Vector2d(0, c.y // self.grid.y)
        # r + d = 2l
        return l + (r * self.pos.x) + (d * self.pos.y) - c // 2
    
    def get_size(self, game_object: GameObject) -> Vector2d:
        c = game_object.parent.get_component(SurfaceComponent).size
        return Vector2d(c.x // self.grid.x, c.y // self.grid.y)

def create_game_object(
        parent = GameObject.root,
        tags: list[str] = [],
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        size: Vector2d|tuple[int, int] = Vector2d(0, 0),
        color: tuple[int, int, int]|None = None,
        shape: Shape|None = None,
        width: int|None = None,
        radius: int|None = None,
        margin: Vector2d = Vector2d(0, 0)) -> GameObject:
    t = GameObject(tags)
    t.disable()
    parent.add_child(t)
    if not isinstance(size, Vector2d):
        size = Vector2d.from_tuple(size)
    if color is not None:
        t.add_component(ColorComponent(color))
    if isinstance(at, Position):
        pos = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size)
    elif isinstance(at, Vector2d):
        pos = at
    elif isinstance(at, InGrid):
        pos = at.get_pos(t)
        size = at.get_size(t)
    else:
        pos = Vector2d.from_tuple(at)
    if shape is not None:
        if shape is Shape.RECTBORDER:
            t.add_component(shape.value(size=size-margin*2, width=width))
        elif shape is Shape.RECT:
            t.add_component(shape.value(size=size-margin*2))
        elif shape is Shape.CIRCLE:
            t.add_component(shape.value(radius=radius))
    t.add_component(Transform(pos))
    t.add_component(SurfaceComponent(size=size))
    t.enable()
    return t

def create_label(
        parent = GameObject.root,
        tags: list[str] = [],
        text: str  = "",
        font: pg.font.Font|None = None,
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        color: tuple[int, int, int]|None = None,
        margin: Vector2d = Vector2d(0, 0)) -> GameObject:
    t = GameObject(tags)
    t.disable()
    parent.add_child(t)
    if color is not None:
        t.add_component(ColorComponent(color))
    l = LabelComponent(text, font)
    size = Vector2d.from_tuple(l.font.size(text))
    t.add_component(l)
    if isinstance(at, Position):
        pos = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size - margin * 2)
    elif isinstance(at, Vector2d):
        pos = at
    elif isinstance(at, InGrid):
        pos = at.get_pos(t)
        size = at.get_size(t)
    else:
        pos = Vector2d.from_tuple(at)
    t.add_component(Transform(pos))
    t.add_component(SurfaceComponent(size=size))
    t.enable()
    return t