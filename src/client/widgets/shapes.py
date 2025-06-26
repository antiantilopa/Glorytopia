from engine_antiantilopa import Component, ShapeComponent, ColorComponent, SurfaceComponent, Vector2d
import pygame as pg



class RectBorderShapeComponent(ShapeComponent):
    size: Vector2d
    width: float
    need_draw: bool

    def __init__(self, size: Vector2d, width: float, need_draw: bool = True) -> None:
        def collide_formula(pos: Vector2d) -> bool:
            return (2 * abs(pos.x) <= size.x and 2 * abs(pos.y) <= size.y) and not (2 * abs(pos.x) <= size.x - 2 * self.width and 2 * abs(pos.y) <= size.y - 2 * self.width)
        super().__init__(collide_formula)
        self.size = size
        self.width = width
        self.need_draw = need_draw

    def draw(self):
        if not self.need_draw:
            return
        if self.game_object.contains_component(ColorComponent):
            pg.draw.rect(
                surface=self.game_object.get_component(SurfaceComponent).pg_surf, 
                color=self.game_object.get_component(ColorComponent).color, 
                rect=((((self.game_object.get_component(SurfaceComponent).size - self.size) / 2)).as_tuple() + self.size.as_tuple()),
                width=self.width
            )

    def __str__(self):
        return f"RectBorderComponent: {self.size}"
    
class LineComponent(ShapeComponent):
    start: Vector2d
    end: Vector2d
    width: float
    need_draw: bool

    def __init__(self, start: Vector2d, end: Vector2d, width: float, need_draw: bool = True) -> None:
        def collide_formula(_) -> bool:
            return False  # Lines do not collide with points. at least not in the current implementation
        if end == start:
            raise ValueError("Start and end points of a line cannot be the same.")
        super().__init__(collide_formula)
        self.start = start
        self.end = end
        self.width = width
        self.need_draw = need_draw

    def draw(self):
        if not self.need_draw:
            return
        if self.game_object.contains_component(ColorComponent):
            pg.draw.line(
                surface=self.game_object.get_component(SurfaceComponent).pg_surf,
                color=self.game_object.get_component(ColorComponent).color,
                start_pos=(self.start + self.game_object.get_component(SurfaceComponent).size // 2).as_tuple(),
                end_pos=(self.end + self.game_object.get_component(SurfaceComponent).size // 2).as_tuple(),
                width=self.width
            )

    def __str__(self):
        return f"LineComponent: {self.start} to {self.end}"