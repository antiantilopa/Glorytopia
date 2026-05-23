from client.globals.window_size import WindowSize
from client.widgets.fastgameobjectcreator import *
from shared.asset_types import TechNode

from engine_antiantilopa import GameObject
from client.texture_assign.texture_assign import TextureAssignSystem


COLORS = (
    ColorComponent.RED,
    ColorComponent.YELLOW,
    ColorComponent.GREEN,
)
LINE_COLORS = (
    ColorComponent.RED,
    ColorComponent.RED,
    ColorComponent.GREEN,
)

@TextureAssignSystem.register_assign_default(TechNode)
def assign_tech_texture(tech: TechNode, tech_obj: GameObject, flags: set[str] = set(), args: tuple[int, list[GameObject]] = (False, [])):
    if args is None:
        args = (False, [])
    color_ind, lines = args
    tech_sprite = create_game_object(
        parent=tech_obj, 
        tags="texture:tech:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        surface_margin=Vector2d(5, 5) if "selector" not in flags else Vector2d(0, 0),
        layer=1
    )
    tech_sprite.add_component(SpriteComponent(nickname=f"techs:{tech.name}", size=WindowSize.get_block_size()))
    for line in lines:
        line.get_component(ColorComponent).color = LINE_COLORS[color_ind]
        line.need_blit_set_true()
    if "selector" in flags:
        return
    create_game_object(
        parent=tech_obj, 
        tags="texture:tech:background", 
        at=InGrid((1, 1), (0, 0)),
        shape=Shape.RECT, 
        color=COLORS[color_ind],
        layer=0,
    )

@TextureAssignSystem.register_update_default(TechNode)
def assign_tech_texture(tech: TechNode, tech_obj: GameObject, flags: set[str] = set(), args: tuple[int, list[GameObject]] = (False, [])):
    if args is None:
        args = (False, [])
    color_ind, lines = args
    if "selector" in flags:
        return
    for child in tech_obj.childs:
        if "texture:tech:background" in child.tags:
            child.get_component(ColorComponent).color = COLORS[color_ind]
            child.need_draw_set_true()
            child.need_blit_set_true()
            break

    for line in lines:
        line.get_component(ColorComponent).color = LINE_COLORS[color_ind]
        line.need_draw_set_true()
        line.need_blit_set_true()