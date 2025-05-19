from serializator.client import Respond
from serializator.data_format import Format
from .client import Client

from shared import *

respond = Respond("GAME")

@respond.event("UPDATE/UNIT")
def update_unit(self: Client, message: tuple[tuple[int, int], SerializedUnit]):
    if len(message[0]) != 0:
        i = 0
        while i < len(self.units):
            unit = self.units[i]
            if unit.pos.as_tuple() == message[0]:
                self.units.pop(i)
                i -= 1
            i += 1
    if len(message[1]) != 0:
        unit = UnitData.from_serializable(message[1])
        self.units.append(unit)
    self.updated = True


@respond.event("UPDATE/CITY")
def update_city(self: Client, message: tuple[SerializedCity]):
    city = CityData.from_serializable(message[0])
    found = False
    for c in self.cities:
        if c.pos == city.pos:
            c = city
            found = True
            break
    if not found:
        self.cities.append(city)
    self.updated = True

@respond.event("UPDATE/TILE")
def update_tile(self: Client, message: tuple[SerializedTile]):
    tile = TileData.from_serializable(message[0])
    self.world[tile.pos.inty()][tile.pos.intx()] = tile
    self.updated = True

@respond.event("UPDATE/TECH")
def update_tech(self: Client, message: tuple[int]):
    self.techs.append(TechNode.by_id(message[0]))
    self.updated = True

@respond.event("END_TURN")
def end_turn(self: Client, message: tuple[str]):
    self.now_playing += 1
    self.now_playing %= len(self.names)
    self.updated = True
