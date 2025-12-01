from client.network.client import GameClient, GamePlayer, GameClientRouter
from shared import *

from . import selector
from . import ui

def main():

    router = GameClientRouter("GAME")

    @router.response("MONEY", datatype=int)
    def money(data: int):
        GameClient.object.me.money = data
        ui.update_money_label(data)

    @router.response("TECHS", datatype=list[TechNode])
    def update_tech(data: list[TechNode]):
        GameClient.object.me.techs = data
        selector.selector_info_update()

    @router.event("UPDATE_MONEY", datatype=int)
    def update_money(data: int):
        GameClient.object.me.money = data
        ui.update_money_label(data)
        
    @router.event("UPDATE_TECH", datatype=TechNode)
    def update_tech(data: TechNode):
        GameClient.object.me.techs.append(data)
        selector.selector_info_update()

    @router.event("END_TURN", datatype=int)
    def end_turn(data: int):
        GameClient.object.now_playing_player_id = data
        ui.update_end_turn_button(GameClient.object.me.id == data)
        ui.update_now_playing_label(GamePlayer.by_id(data).nickname)

    @router.event("RECONNECT", datatype=str)
    def update_money(data: str):
        GameClient.object.me.money = data
        ui.update_money_label(data)

    @router.response("SYNCHRONIZE")
    def synchronize(data: None):
        ui.update_money_label(GameClient.object.me.money)
        selector.selector_info_update()