from engine_antiantilopa import *
from client.network.client import GamePlayer
from client.widgets.fastgameobjectcreator import *
from shared import *
from shared.util.position import Pos
from . import game_classes
from . import components

class FogOfWarComponent(Component):
    size: Pos
    objs: list[list[GameObject|None]]

    def __init__(self, size: Pos):
        Component.__init__(self)
        self.size = size
        self.objs = [[None for _ in range(size.x)] for _ in range(size.y)]

    def set_fog(self, pos: Pos):
        if self.objs[pos.inty()][pos.intx()] is not None:
            return
        if game_classes.Tile.tile_map[pos.inty()][pos.intx()] is None:
            return
        self.objs[pos.inty()][pos.intx()] = _create_fog(pos)
    
    def destroy_fog(self, pos: Pos):
        if self.objs[pos.inty()][pos.intx()] is None:
            return
        self.objs[pos.inty()][pos.intx()].destroy()
        self.objs[pos.inty()][pos.intx()] = None

def update_fog(player: GamePlayer):
    fog_of_war_component = GameObject.get_game_object_by_tags("game_screen:world_section:world:fog_of_war_layer").get_component(FogOfWarComponent)

    for i in range(game_classes.GameRules.world_size.y):
        for j in range(game_classes.GameRules.world_size.x):
            if player.vision[i][j] == 0:
                fog_of_war_component.set_fog(Pos(j, i))
            elif player.vision[i][j] == 1:
                fog_of_war_component.destroy_fog(Pos(j, i))

def _create_fog(pos: Pos) -> GameObject:
    # not used untill vision is full
    fog_of_war_layer = GameObject.get_game_object_by_tags("game_screen:world_section:world:fog_of_war_layer")

    fog = create_game_object(
        parent=fog_of_war_layer,
        tags="FOG",
        at=InGrid(game_classes.GameRules.world_size.as_tuple(), pos.as_tuple()),
        shape=Shape.RECT,
        color=(128, 128, 128)
    )
    fog.add_component(components.PositionComponent(pos))
    fog.get_component(SurfaceComponent).pg_surf.set_alpha(128)
    return fog