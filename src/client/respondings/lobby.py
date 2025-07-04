from serializator.client import Respond
from serializator.data_format import Format
from .client import Client, UpdateCodes
import copy

respond = Respond("LOBBY")

@respond.event("JOIN")
def join(self: Client, message: tuple[str]):
    for name in self.readiness:
        self.readiness[name] = False
    self.readiness[message[0]] = False
    self.names.append(message[0])
    self.order[len(self.order)] = message[0]
    self.names_to_colors[message[0]] = 0 # just to ensure that the client do not try to draw the non existent color
    if message[0] == self.myname:
        self.joined = True
    self.updated |= 2 ** UpdateCodes.JOIN.value

@respond.error("JOIN")
def join(self: Client, message: tuple[str]):
    self.joined = False
    print(f"Error while joining: {message[0]}")

@respond.event("RECONNECT")
def join(self: Client, message: tuple[str]):
    if message[0] == self.myname:
        self.joined = True
        self.updated |= 2 ** UpdateCodes.RECONNECT.value

@respond.error("RECONNECT")
def join(self: Client, message: tuple[str]):
    self.joined = False
    print(f"Error while reconnecting: {message[0]}")

@respond.event("READY")
def ready(self: Client, message: tuple[str, int]):
    self.readiness[message[0]] = message[1]
    self.updated |= 2 ** UpdateCodes.READY.value

@respond.event("MESSAGE")
def message(self: Client, message: tuple[str, str]):
    self.messages.append(message)
    self.updated |= 2 ** UpdateCodes.MESSAGE.value

@respond.event("COLOR_CHANGE")
def color_change(self: Client, message: tuple[str, int]):
    self.names_to_colors[message[0]] = message[1]
    self.updated |= 2 ** UpdateCodes.COLOR_CHANGE.value

@respond.event("GAME_START")
def game_start(self: Client, message: tuple[int]):
    if message[0] == 0:
        self.game_started = True
        self.send(Format.request("GAME/WORLD", []))
        self.send(Format.request("GAME/CITIES", []))
        self.send(Format.request("GAME/UNITS", []))
        self.send(Format.request("GAME/ME/MONEY", []))
        self.updated |= 2 ** UpdateCodes.GAME_START.value
    else:
        self.messages.append(("", str(message[0])))

@respond.info("READINESS")
def info_readiness(self: Client, message: list[tuple[str, bool]]):
    for (key, value) in message:
        self.readiness[key] = value

@respond.info("NAMES")
def info_names(self: Client, message: list[str]):
    self.names = copy.deepcopy(message)
    for name in message:
        if name not in self.readiness:
            self.readiness[name] = False
    self.updated |= 2 ** UpdateCodes.INIT_NAMES.value

@respond.info("COLORS")
def info_colors(self: Client, message: list[tuple[str, int]]):
    self.names_to_colors = {name: color for (name, color) in message}
    self.updated |= 2 ** UpdateCodes.INIT_COLORS.value
