from client.actions.action import ActionSystem
from client.network.client import GameClient
from netio.serialization.routing import MessageType
from shared.asset_types import UnitType
from shared.unit import UnitData


@ActionSystem.register_action_default(UnitData)
def heal(obj: UnitData, *_):
    def do_heal(args: list):
        GameClient.object.send_message(MessageType.EVENT, "GAME/ACTION", [obj, 1269223])
    if obj.attacked or obj.moved:
        return
    if obj.type == UnitType.get("mindbender"):
        return [("heal", do_heal)]