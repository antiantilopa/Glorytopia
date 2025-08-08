from engine_antiantilopa import *
from ..widgets.shapes import RectBorderShapeComponent, LineComponent
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
    size: Vector2d

    def __init__(self, grid: Vector2d|tuple[int, int], pos: Vector2d|tuple[int, int], size: Vector2d|tuple[int, int] = Vector2d(1, 1)):
        if isinstance(grid, Vector2d):
            self.grid = grid
        else:
            self.grid = Vector2d.from_tuple(grid)
        if isinstance(pos, Vector2d):
            self.pos = pos
        else:
            self.pos = Vector2d.from_tuple(pos)
        if isinstance(size, Vector2d):
            self.size = size
        else:
            self.size = Vector2d.from_tuple(size)

    def get_pos(self, game_object: GameObject, surface_margin: Vector2d = Vector2d(0, 0)) -> Vector2d:
        c = game_object.parent.get_component(SurfaceComponent).size - 2 * surface_margin
        l = Vector2d(c.x / self.grid.x, c.y / self.grid.y) / 2
        r = Vector2d(c.x / self.grid.x, 0)
        d = Vector2d(0, c.y / self.grid.y)
        # r + d = 2l
        result = (l * self.size) + (r * self.pos.x) + (d * self.pos.y) - c / 2
        return Vector2d(round(result.x), round(result.y))

    def get_size(self, game_object: GameObject, surface_margin: Vector2d = Vector2d(0, 0)) -> Vector2d:
        c = game_object.parent.get_component(SurfaceComponent).size - 2 * surface_margin
        return Vector2d(c.x * self.size.x // self.grid.x, c.y * self.size.y // self.grid.y)

def create_game_object(
        parent = GameObject.root,
        tags: list[str] = [],
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        size: Vector2d|tuple[int, int] = Vector2d(0, 0),
        color: tuple[int, int, int]|None = None,
        shape: Shape|None = None,
        width: int|None = None,
        radius: int|None = None,
        margin: Vector2d = Vector2d(0, 0),
        layer: int = 1,
        surface_margin: Vector2d = Vector2d(0, 0),
        crop: bool = True) -> GameObject:
    t = GameObject(tags)
    t.disable()
    parent.add_child(t)
    if not isinstance(size, Vector2d):
        size = Vector2d.from_tuple(size)
    if color is not None:
        t.add_component(ColorComponent(color))
    if isinstance(at, Position):
        pos = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size - 2 * surface_margin)
    elif isinstance(at, Vector2d):
        pos = at
    elif isinstance(at, InGrid):
        pos = at.get_pos(t, surface_margin)
        size = at.get_size(t, surface_margin)
    else:
        pos = Vector2d.from_tuple(at)
    if shape is not None:
        if color is None: need_draw = False
        else: need_draw = True
        if shape is Shape.RECTBORDER:
            t.add_component(shape.value(size=size-margin*2, width=width, need_draw=need_draw))
        elif shape is Shape.RECT:
            t.add_component(shape.value(size=size-margin*2, need_draw=need_draw))
        elif shape is Shape.CIRCLE:
            t.add_component(shape.value(radius=radius, need_draw=need_draw))
    t.add_component(Transform(pos))
    t.add_component(SurfaceComponent(size=size, crop=crop, layer=layer))
    t.enable()
    return t

def create_label(
        color: tuple[int, int, int],
        parent = GameObject.root,
        tags: list[str] = [],
        text: str  = "",
        font: pg.font.Font|None = None,
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        margin: Vector2d = Vector2d(0, 0),
        layer: int = 1,
        crop: bool = True) -> GameObject:
    try:
        t = GameObject(tags)
        t.disable()
        parent.add_child(t)
        l = LabelComponent(text, font)
        size = Vector2d.from_tuple(l.font.size(text))
        t.add_component(l)
        t.add_component(ColorComponent(color))
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
        t.add_component(SurfaceComponent(size=size, crop=crop, layer=layer))
        t.enable()
        return t
    except Exception as e:
        t.destroy()
        raise e

def create_line_game_object(
        color: tuple[int, int, int],
        parent = GameObject.root,
        tags: list[str] = [],
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        to: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        width: int|None = None,
        margin: Vector2d = Vector2d(0, 0),
        layer: int = 1,
        crop: bool = True) -> GameObject:
    try:
        t = GameObject(tags)
        t.disable()
        parent.add_child(t)
        t.add_component(ColorComponent(color))
        if isinstance(at, Position):
            start = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size - margin * 2)
        elif isinstance(at, Vector2d):
            start = at
        elif isinstance(at, InGrid):
            start = at.get_pos(t)
        else:
            start = Vector2d.from_tuple(to)
        if isinstance(to, Position):
            end = Position.get_vector_pos(to, size, parent.get_component(SurfaceComponent).size - margin * 2)
        elif isinstance(to, Vector2d):
            end = to
        elif isinstance(to, InGrid):
            end = to.get_pos(t)
        else:
            end = Vector2d.from_tuple(to)
        size = Vector2d(abs((end - start).x), abs((end - start).y)) + Vector2d(width, width) if width is not None else Vector2d(1, 1)
        t.add_component(LineComponent((start - end) / 2, (end - start) / 2, width=width if width is not None else 1))
        t.add_component(Transform((start + end) / 2))
        t.add_component(SurfaceComponent(size=size, crop=crop, layer=layer))
        t.enable()
        return t
    except Exception as e:
        t.destroy()
        raise e

def create_label_block(
        color: tuple[int, int, int],
        parent = GameObject.root,
        tags: list[str] = [],
        text: str  = "",
        font: pg.font.Font | None = None,
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        text_pos: Position = Position.CENTER,
        margin: Vector2d = Vector2d(0, 0),
        layer: int = 1, 
        crop: bool = True) -> GameObject:
    if text_pos not in (Position.LEFT, Position.CENTER, Position.RIGHT):
        raise ValueError("text_pos have to be either LEFT, CENTER, or RIGHT.")
    
    t = GameObject(tags)
    t.disable()
    parent.add_child(t)

    if font is None:
        font = pg.font.SysFont("consolas", 30)

    
    max_length = max(map(lambda x: font.size(x)[0], text.split("\n")))
    total_height = sum(map(lambda x: font.size(x)[1], text.split("\n")))
    
    size = Vector2d(max_length, total_height)

    if isinstance(at, Position):
        pos = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size - margin * 2)
    elif isinstance(at, Vector2d):
        pos = at
    elif isinstance(at, InGrid):
        pos = at.get_pos(t)
    else:
        pos = Vector2d.from_tuple(at)

    t.add_component(SurfaceComponent(size=size, layer=layer, crop=crop))
    t.add_component(Transform(pos))

    if isinstance(tags, str):
        new_tag = tags + ":label"
    elif len(tags) == 0:
        new_tag = "label"
    else:
        new_tag = tags[0] + ":label"

    for i in range(len(text.split("\n"))):
        line = text.split("\n")[i]
        l = create_label(color, t, new_tag, line, font, Position.CENTER)
        label_pos_x = Position.get_vector_pos(text_pos, Vector2d.from_tuple(font.size(line)), size).x
        label_pos_y = InGrid((1, len(text.split("\n"))), (0, i), (1, 1)).get_pos(l).y
        l.get_component(Transform).set_pos(Vector2d(label_pos_x, label_pos_y))

    t.enable()
    return t
    
def create_list_game_object(
        parent = GameObject.root,
        tags: list[str] = [],
        at: Vector2d|tuple[int, int]|Position|InGrid = Vector2d(0, 0),
        size: Vector2d|tuple[int, int] = Vector2d(0, 0),
        color: tuple[int, int, int]|None = None,
        shape: Shape|None = None,
        width: int|None = None,
        radius: int|None = None,
        margin: Vector2d = Vector2d(0, 0),
        layer: int = 1,
        surface_margin: Vector2d = Vector2d(0, 0), 
        axis: tuple[bool, bool] = (0, 1), 
        x_axis_keys: tuple[int, int] = (pg.K_LEFT, pg.K_RIGHT),
        y_axis_keys: tuple[int, int] = (pg.K_UP, pg.K_DOWN),
        speed: Vector2d = Vector2d(10, 10),
        listen_for_hold: bool = True,
        on_press: bool = True,
        bound: bool = True) -> GameObject:

    t = GameObject(tags)
    t.disable()
    parent.add_child(t)

    if not isinstance(size, Vector2d):
        size = Vector2d.from_tuple(size)
        
    if color is not None:
        t.add_component(ColorComponent(color))

    if isinstance(at, Position):
        pos = Position.get_vector_pos(at, size, parent.get_component(SurfaceComponent).size - 2 * surface_margin)
    elif isinstance(at, Vector2d):
        pos = at
    elif isinstance(at, InGrid):
        pos = at.get_pos(t, surface_margin)
        size = at.get_size(t, surface_margin)
    else:
        pos = Vector2d.from_tuple(at)
        
    if shape is not None:
        if color is None: need_draw = False
        else: need_draw = True
        if shape is Shape.RECTBORDER:
            t.add_component(shape.value(size=size-margin*2, width=width, need_draw=need_draw))
        elif shape is Shape.RECT:
            t.add_component(shape.value(size=size-margin*2, need_draw=need_draw))
        elif shape is Shape.CIRCLE:
            t.add_component(shape.value(radius=radius, need_draw=need_draw))
    t.add_component(Transform(pos))
    t.add_component(SurfaceComponent(size=size, layer=layer))

    def scroll(g_obj: GameObject, keys: list[int], *_):
        if len(g_obj.childs) == 0:
            return
        delta = Vector2d(0, 0)
        if axis[0]:
            if x_axis_keys[0] in keys:
                delta = delta + speed * Vector2d(+1, 0)
            elif x_axis_keys[1] in keys:
                delta = delta + speed * Vector2d(-1, 0)

        if axis[1]:
            if y_axis_keys[0] in keys:
                delta = delta + speed * Vector2d(0, +1)
            elif y_axis_keys[1] in keys:
                delta = delta + speed * Vector2d(0, -1)
        if bound:
            if axis[0] and delta.x != 0:
                g = max(g_obj.childs, key=lambda g: g.get_component(Transform).pos.x + g.get_component(SurfaceComponent).size.x/2)
                b_r = (g_obj.get_component(SurfaceComponent).size.x / 2) - (g.get_component(Transform).pos.x + g.get_component(SurfaceComponent).size.x / 2)
                g = min(g_obj.childs, key=lambda g: g.get_component(Transform).pos.x - g.get_component(SurfaceComponent).size.x/2)
                b_l = (-g_obj.get_component(SurfaceComponent).size.x / 2) - (g.get_component(Transform).pos.x - g.get_component(SurfaceComponent).size.x / 2)
                if b_l - b_r > 0:
                    if b_l < delta.x:
                        delta.x = b_l
                    if b_r > delta.x:
                        delta.x = b_r
                elif b_l - b_r < 0:
                    if b_l > delta.x:
                        delta.x = b_l
                    if b_r < delta.x:
                        delta.x = b_r
            if axis[1] and delta.y != 0:
                g = max(g_obj.childs, key=lambda g: g.get_component(Transform).pos.y + g.get_component(SurfaceComponent).size.y/2)
                b_d = (g_obj.get_component(SurfaceComponent).size.y / 2) - (g.get_component(Transform).pos.y + g.get_component(SurfaceComponent).size.y / 2)
                g = min(g_obj.childs, key=lambda g: g.get_component(Transform).pos.y - g.get_component(SurfaceComponent).size.y/2)
                b_u = (-g_obj.get_component(SurfaceComponent).size.y / 2) - (g.get_component(Transform).pos.y - g.get_component(SurfaceComponent).size.y / 2)
                if b_u - b_d > 0:
                    if b_u < delta.y:
                        delta.y = b_u
                    if b_d > delta.y:
                        delta.y = b_d
                elif b_u - b_d < 0:
                    if b_u > delta.y:
                        delta.y = b_u
                    if b_d < delta.y:
                        delta.y = b_d
            
        if delta != Vector2d(0, 0):
            for child in g_obj.childs:
                child.get_component(Transform).move(delta)

    t.add_component(KeyBindComponent((x_axis_keys + y_axis_keys), listen_for_hold, on_press, scroll))
    t.enable()
    return t
    