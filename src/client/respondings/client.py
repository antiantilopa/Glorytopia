from serializator.client import Client as SerClient
from serializator.client import Respond
from shared import UnitData, CityData, TileData, TechNode
from enum import Enum

class UpdateCodes(Enum):
    NOTHING = 0
    JOIN = 1
    DISCONNECT = 2
    READY = 3
    MESSAGE = 4
    GAME_START = 5
    INIT_NAMES = 6

respond = Respond()
@respond.event("DISCONNECT")
def disconnect(self: "Client", message: tuple[str]):
    for name in self.readiness:
        self.readiness[name] = False
    print(message)
    print(self.names)
    self.readiness.pop(message[0])
    self.names.remove(message[0])
    self.updated |= 2 ** UpdateCodes.DISCONNECT.value

class Client(SerClient):
    object = None
    def __init__(self):
        SerClient.__init__(self)
        self.respond.merge(respond)
        self.names: list[str] = []
        self.readiness: dict[str, bool] = {}
        self.game_started = False
        self.names: list[str] = []
        self.now_playing: int = 0
        self.order: dict[str, int] = {}
        self.messages: list[tuple[str, str]] = []
        self.myname: str = ""

        self.world: list[list[TileData]] = [[(0) for i in range(18)] for j in range(18)]
        self.units: list[UnitData] = []
        self.cities: list[CityData] = []
        self.techs: list[TechNode] = []
        self.money = 0
        self.updated = 0
        Client.object = self

