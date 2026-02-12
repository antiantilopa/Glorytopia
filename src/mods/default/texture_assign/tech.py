from client.globals.window_size import WindowSize
from client.widgets.fastgameobjectcreator import *
from shared.asset_types import TechNode

from engine_antiantilopa import GameObject
from client.texture_assign.texture_assign import TextureAssignSystem

@TextureAssignSystem.register_assign_default(TechNode)
def assign_tech_texture(tech: TechNode, tech_obj: GameObject, flags: set[str] = set()):
    tech_sprite = create_game_object(
        parent=tech_obj, 
        tags="texture:tech:sprite", 
        at=InGrid((1, 1), (0, 0)), 
        layer=0
    )
    tech_sprite.add_component(SpriteComponent(nickname=f"techs:{tech.name}", size=WindowSize.get_block_size()))