from serializator.client import Respond
from serializator.data_format import Format
from .client import Client, UpdateCodes

from shared import *
from typing import Literal
from engine_antiantilopa import Vector2d

respond = Respond("GAME")

@respond.event("UPDATE/UNIT")
def update_unit(self: Client, message: tuple[tuple[int, int]|tuple, SerializedUnit|tuple]):
    if len(message[0]) != 0:
        i = 0
        while i < len(self.units):
            unit = self.units[i]
            if unit.pos == Vector2d.from_tuple(message[0]):
                if len(message[1]) == 0:
                    self.units.pop(i)
                    unit = ()
                else:
                    self.units[i] = UnitData.from_serializable(message[1])
                    unit = self.units[i]
                break
            i += 1
    elif len(message[1]) != 0:
        unit = UnitData.from_serializable(message[1])
        self.units.append(unit)
    else: 
        return # means nothing changed. If we are here, then we have a bug.
    if len(message[1]) == 0: unit = ()
    self.units_updates.append((message[0], unit))
    self.updated |= 2 ** UpdateCodes.UPDATE_UNIT.value


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
    self.cities_updates.append(city)
    self.updated |= 2 ** UpdateCodes.UPDATE_CITY.value

@respond.event("UPDATE/TILE")
def update_tile(self: Client, message: tuple[SerializedTile]):
    tile = TileData.from_serializable(message[0])
    self.world[tile.pos.inty()][tile.pos.intx()] = tile
    self.world_updates.append((tile.pos.intx(), tile.pos.inty()))
    self.updated |= 2 ** UpdateCodes.UPDATE_TILE.value

@respond.event("UPDATE/TECH")
def update_tech(self: Client, message: tuple[int]):
    self.techs.append(TechNode.by_id(message[0]))
    self.updated |= 2 ** UpdateCodes.UPDATE_TECH.value

@respond.event("UPDATE/MONEY")
def update_money(self: Client, message: tuple[int]):
    self.money = message[0]
    self.updated |= 2 ** UpdateCodes.UPDATE_MONEY.value

@respond.event("END_TURN")
def end_turn(self: Client, message: tuple[str]):
    self.now_playing += 1
    self.now_playing %= len(self.names)
    self.updated |= 2 ** UpdateCodes.END_TURN.value

@respond.event("GAME_START")
def game_start(self: Client, message: tuple[int]):
    self.game_started = True
    self.send(Format.request("GAME/WORLD_SIZE", []))
    self.send(Format.request("GAME/WORLD", []))
    self.send(Format.request("GAME/CITIES", []))
    self.send(Format.request("GAME/UNITS", []))
    self.send(Format.request("GAME/MY_MONEY", []))
    self.updated |= 2 ** UpdateCodes.GAME_START.value
