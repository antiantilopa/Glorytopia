







from client.globals.window_size import WindowSize
from client.scenes.game_screen.game_classes import City
from shared.city import CityData
from engine_antiantilopa import GameObject
from client.widgets.fastgameobjectcreator import *
from client.network.client import GamePlayer
from client.texture_assign.texture_assign import TextureAssignSystem

@TextureAssignSystem.register_assign_default(CityData)
def assign_city_texture(city: City, city_obj: GameObject, flags: set[str] = set()):
    city_sprite = create_game_object(
        parent=city_obj, 
        tags="texture:city:sprite", 
        size=WindowSize.get_block_size(), 
        layer=0
    )
    city_sprite.add_component(SpriteComponent(nickname="city:city", size=WindowSize.get_block_size()))
    if "selector" in flags:
        return
    _update_city_name_label(city, city_obj)
    _update_city_upgrades(city, city_obj)

@TextureAssignSystem.register_update_default(CityData)
def update_city_texture(city: City, city_obj: GameObject, flags: set[str] = set()):
    _update_city_name_label(city, city_obj)
    _update_city_upgrades(city, city_obj)

def _update_city_name_label(city: City, city_obj: GameObject):
    city_owner = city.owner
    if city_owner == -1:
        return

    i = 0
    while i < len(city_obj.childs):
        if "texture:city:name_label" in city_obj.childs[i].tags:
            city_obj.childs[i].destroy()
        elif "texture:city:name_label_background" in city_obj.childs[i].tags:
            city_obj.childs[i].destroy()
        else:
            i += 1
            
    city_name_label = create_label(
        parent=city_obj, 
        tags="texture:city:name_label", 
        text=f"{city.level} {city.name}{("!" if city.is_capital else "")}", 
        font=pg.font.SysFont("consolas", WindowSize.get_block_size().intx() // 6), 
        at=Position.DOWN, 
        color=GamePlayer.by_id(city.owner).get_secondary_color(), 
        layer=6, 
        crop=0
    )
    create_game_object(
        parent=city_obj, 
        tags="texture:city:name_label_background", 
        at=Position.DOWN, 
        size=city_name_label.get_component(SurfaceComponent).size, 
        shape=Shape.RECT, 
        color=GamePlayer.by_id(city.owner).get_main_color(), 
        layer=5, 
        crop=0
    )

def _update_city_upgrades(city: City, city_obj: GameObject):
    found_forge = any("texture:city:forge_sprite" in child.tags for child in city_obj.childs)
    found_walls = any("texture:city:walls_sprite" in child.tags for child in city_obj.childs)
    
    if not found_forge and city.forge:
        forge_sprite = create_game_object(
            parent=city_obj, 
            tags="texture:city:forge_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=1
        )
        forge_sprite.add_component(SpriteComponent(nickname="city:city_forge", size=WindowSize.get_block_size()))
        
    if not found_walls and city.walls:
        walls_sprite = create_game_object(
            parent=city_obj, 
            tags="texture:city:walls_sprite", 
            at=InGrid((1, 1), (0, 0)), 
            layer=2
        )
        walls_sprite.add_component(SpriteComponent(nickname="city:city_walls", size=WindowSize.get_block_size()))
        