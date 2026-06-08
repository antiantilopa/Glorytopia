from client.actions.action import ActionSystem
from client.network.client import GameClient
from netio.serialization.routing import MessageType
from shared.asset_types import TechNode, UnitType
from shared.player import SharedPlayerData
from shared.unit import UnitData

class __DummyPlayerData(SharedPlayerData):
    techs: list[TechNode]

@ActionSystem.register_action_default(UnitData)
def upgrade(obj: UnitData, player: __DummyPlayerData):
    def upgrade_to_boat(args: list):
        GameClient.object.send_message(MessageType.EVENT, "GAME/ACTION", [obj, 596349512])
    def upgrade_to_galley(args: list):
        GameClient.object.send_message(MessageType.EVENT, "GAME/ACTION", [obj, 596349513])
    def upgrade_to_bomber(args: list):
        GameClient.object.send_message(MessageType.EVENT, "GAME/ACTION", [obj, 596349514])
    if obj.attacked or obj.moved:
        return
    if obj.type != UnitType.get("raft"):
        return
    result = []
    boat_type = UnitType.get("boat")
    galley_type = UnitType.get("galley")
    bomber_type = UnitType.get("bomber")
    found = [0, 0, 0]
    for tech in player.techs:
        if not found[0] and boat_type in tech.units:
            result.append((f"upgrade to boat:{boat_type.cost}", upgrade_to_boat))
            found[0] = 1
        if not found[1] and galley_type in tech.units:
            result.append((f"upgrade to galley:{galley_type.cost}", upgrade_to_galley))
            found[1] = 1
        if not found[2] and bomber_type in tech.units:
            result.append((f"upgrade to bomber:{bomber_type.cost}", upgrade_to_bomber))
            found[2] = 1
        if all(found):
            break
    return result