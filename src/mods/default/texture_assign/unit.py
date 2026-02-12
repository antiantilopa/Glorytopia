

from client.globals.window_size import WindowSize
from client.network.client import GamePlayer
from client.texture_assign.texture_assign import TextureAssignSystem
from shared.unit import UnitData
from engine_antiantilopa import GameObject
from client.widgets.fastgameobjectcreator import *

@TextureAssignSystem.register_assign_default(UnitData)
def assign_unit_texture(unit: UnitData, game_object: GameObject, flags: set[str] = set()):
    sprite = create_game_object(
        parent=game_object,
        tags="texture:unit:sprite",
        at=InGrid((1, 1), (0, 0)), 
        layer=2, 
    )
    sprite.add_component(SpriteComponent(nickname=f"units:{unit.type.name}", size=WindowSize.get_block_size()))

    if "selector" in flags:
        return

    health = create_game_object(
        parent=game_object, 
        tags="texture:unit:health",
        at=Position.LEFT_UP, 
        size=WindowSize.get_block_size() // 3, 
        shape=Shape.CIRCLE, 
        layer=3, 
        color=GamePlayer.by_id(unit.owner).get_main_color(), 
        radius=WindowSize.get_block_size().intx() // 6, 
    )
    create_label(
        parent=health, 
        tags="texture:unit:health:number",
        text=f"{unit.health}", 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 4), 
        color=GamePlayer.by_id(unit.owner).get_secondary_color(), 
    )
    sprite.need_blit_set_true()

@TextureAssignSystem.register_update_default(UnitData)
def update_unit_texture(unit: UnitData, game_object: GameObject, flags: set[str] = set()):
    for child in game_object.childs:
        if "texture:unit:health" in child.tags:
            child.childs[0].destroy()
            create_label(
                parent=child, 
                text=f"{unit.health}", 
                font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 4), 
                color=GamePlayer.by_id(unit.owner).get_secondary_color(),
                tags="texture:unit:health:number"
            )