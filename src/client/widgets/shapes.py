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
                rect=((((Vector2d.from_tuple(self.game_object.get_component(SurfaceComponent).pg_surf.get_size()) - self.size) / 2)).as_tuple() + self.size.as_tuple()),
                width=self.width
            )

    def __str__(self):
        return f"RectBorderComponent: {self.size}"