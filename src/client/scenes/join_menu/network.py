from client.network.client import GameClient, GameClientRouter, GamePlayer
from client.scenes.join_menu import launchers
from client.scenes.join_menu.state import State
from shared.util.position import Pos

def main():
    router = GameClientRouter("LOBBY")

    @router.response("JOIN", datatype=int)
    def join_result(data: int):
        match data:
            case -1: return
            case 0:  launchers.launch_lobby()
            case 1:  State.change_state(2)

    @router.response("RECONNECT", datatype=int)
    def reconnect_result(data: int):
        match data:
            case -1: return
            case 0:  pass # TODO this shit is useless 

    @router.event("RECONNECT", datatype=tuple[int, Pos])
    def reconnect_result(data: tuple[int, Pos]):
        GamePlayer.joined_players.append(GameClient.object.me)
        launchers.launch_game_screen(*data)