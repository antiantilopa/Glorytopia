from client.network.client import GameClient, GamePlayer, GameClientRouter
from shared import *

from . import selector
from . import ui
from . import game_classes
from . import fog_of_war

def main():

    router = GameClientRouter("GAME")

    @router.response("MONEY", datatype=int)
    def money(data: int):
        GameClient.object.me.money = data
        ui.update_money_label(data)

    @router.response("TECHS", datatype=list[TechNode])
    def tech(data: list[TechNode]):
        GameClient.object.me.techs = data
        selector.selector_info_update()

    @router.event("VISION", datatype=list[int])
    def vision(data: list[int]):
        line_vision = list_int32_to_list_bool(data)
        GameClient.object.me.set_vision(line_vision, game_classes.GameRules.world_size)
        selector.selector_info_update()
        game_classes.update_fog(GameClient.object.me)

    @router.event("UPDATE_MONEY", datatype=int)
    def update_money(data: int):
        GameClient.object.me.money = data
        ui.update_money_label(data)
        
    @router.event("UPDATE_TECH", datatype=TechNode)
    def update_tech(data: TechNode):
        GameClient.object.me.techs.append(data)
        selector.selector_info_update()

    @router.event("UPDATE_VISION", datatype=list[int])
    def update_vision(data: list[int]):
        line_vision = list_int32_to_list_bool(data)
        GameClient.object.me.set_vision(line_vision, game_classes.GameRules.world_size)
        selector.selector_info_update()
        fog_of_war.update_fog(GameClient.object.me)

    @router.event("END_TURN", datatype=int)
    def end_turn(data: int):
        GameClient.object.now_playing_player_id = data
        ui.update_end_turn_button(GameClient.object.me.id == data)
        ui.update_now_playing_label(GamePlayer.by_id(data).nickname)

    @router.event("RECONNECT", datatype=str)
    def update_money(data: str):
        print(f"{data} reconnected to the game")

    @router.response("SYNCHRONIZE")
    def synchronize(data: None):
        ui.update_money_label(GameClient.object.me.money)
        selector.selector_info_update()

def list_int32_to_list_bool(x: list[int]) -> list[bool]:
    result = []
    for num in reversed(x):
        for j in range(32):
            result.append(1 & num)
            num = num >> 1
    result.reverse()
    return result