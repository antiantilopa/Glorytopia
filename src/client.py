from serializator.client import Client, Format
from serializator.net import int_to_flags
import copy
import pygame as pg
pg.init()
mc = Client()

names: list[str]
readiness: dict[str, bool]
screen: pg.Surface = None
game_started = False
names = []
readiness = {}

world = [[(0) for i in range(18)] for j in range(18)]
units = []
cities = []

def start_the_game():
    global game_started
    game_started = True

@mc.respond.disconnection()
def disc(self: Client):
    print("DISCONNECTION!!!")
    self.sock.close()

@mc.respond.error()
def route_err(self: Client, message: tuple[str]):
    print("!!!")
    print(*message)
    print("!!!")

@mc.respond.info()
def default(self: Client, message: tuple):
    print(message)

@mc.respond.event("GAME/UPDATE/UNIT")
def game_updtae_unit(self: Client, message: tuple[tuple|tuple[int, int], tuple|tuple[int, int, tuple[int, int], int, int]]):
    print("EVENT:GAME/UPDATE/UNIT", message)
    if len(message[0]) != 0:
        i = 0
        while i < len(units):
            unit = units[i]
            if unit[2] == message[0]:
                units.pop(i)
                i -= 1
            i += 1
    if len(message[1]) != 0:
        unit = message[1]
        units.append(unit)


@mc.respond.info("READINESS")
def info_readiness(self: Client, message: list[tuple[str, bool]]):
    for (key, value) in message:
        readiness[key] = value

@mc.respond.info("NAMES")
def info_names(self: Client, message: list[str]):
    global names
    names = copy.deepcopy(message)
    for name in message:
        if name not in readiness:
            readiness[name] = False

@mc.respond.event("MESSAGE")
def message(self: Client, message: tuple[str, str]):
    print(f"<{message[0]}> {message[1]}")

@mc.respond.event("DISCONNECT")
def disconnect(self, message: tuple[str]):
    print(f'{message[0]} has disconnected')
    for name in readiness:
        readiness[name] = False
    readiness.pop(message[0])
    names.remove(message[0])

@mc.respond.event("JOIN")
def join(self, message: tuple[str]):
    print(f'{message[0]} has connected')
    for name in readiness:
        readiness[name] = False
    readiness[message[0]] = False
    names.append(message[0])

@mc.respond.event("GAME/GAME_START")
def game_start(self, message):
    print(message, "...")
    if message[0] == 0:
        pass
        start_the_game()
        mc.send(Format.request("GAME/WORLD", []))
        mc.send(Format.request("GAME/CITIES", []))
        mc.send(Format.request("GAME/UNITS", []))
        mc.send(Format.request("GAME/ME/MONEY", []))
    else:
        print(message[0], "...")

@mc.respond.info("GAME/WORLD")
def print_world(self, message: list[tuple[int, int, tuple[int, int], int, int, bool]]):
    global world
    for tile in message:
        world[tile[2][1]][tile[2][0]] = (tile[0], tile[3], tile[4])

@mc.respond.info("GAME/UNITS")
def print_units(self, message: list[tuple[int, int, tuple[int, int], int, int]]):
    global units
    units = []
    for unit in message:
        print(f"unit: pos = {unit[2]}, type = {unit[0]}, owner = {unit[1]}, hp = {unit[3]} flags = {unit[4]}")
        units.append((unit[0], unit[1], unit[2], unit[3]))

@mc.respond.info("GAME/CITIES")
def print_cities(self, message: list[tuple[str, int, tuple[int, int]]]):
    global cities
    for city in message:
        print(f"city: pos = {city[2]}, name = {city[0]}, owner = {city[1]}, level = {city[3]}")
        cities.append((city[0], city[1], city[2], city[3]))

@mc.respond.info("GAME/ME/TECHS")
def print_techs(self, message: tuple[int]):
    print(f"techs = {message}")

@mc.respond.info("GAME/ME/CITIES")
def print_cities(self, message: list[tuple[str, int, tuple[int, int]]]):
    for city in message:
        print(f"my city: pos = {city[2]}, name = {city[0]}, owner = {city[1]}, level = {city[3]}")

@mc.respond.info("GAME/ME/UNITS")
def print_units(self, message: list[tuple[int, int, tuple[int, int], int, int]]):
    for unit in message:
        print(f"my unit: pos = {unit[2]}, type = {unit[0]}, owner = {unit[1]}, hp = {unit[3]}, flags = {unit[5]}")

@mc.respond.info("GAME/ME/VISION")
def print_units(self, message: list[int]):
    for row in message:
        print(*["?#"[int(i)] for i in int_to_flags(row, 18)])

@mc.respond.info("GAME/ME/MONEY")
def print_units(self, message: list[int]):
    print(f"money = {message[0]}")

@mc.respond.info("ORDER")
def print_order(self, message: list[str]):
    print("order is:")
    for name in message:
        print("    "+ name)

@mc.respond.info("GAME/END_TURN")
def print_end_turn(self, message: tuple[str]):
    print(f"{message[0]} has ended their turn")

@mc.respond.event("GAME/UPDATE/UNIT")
def update_unit(self, message: tuple[tuple|tuple[int, int], tuple|tuple[int, int, tuple[int, int], int, int]]):
    if len(message[0]) != 0:
        i = 0
        while i < len(units):
            unit = units[i]
            if unit[2] == message[0]:
                units.pop(i)
                i -= 1
            i += 1
    if len(message[1]) != 0:
        unit = message[1]
        units.append(unit)

@mc.respond.event("GAME/UPDATE/CITY")
def update_city(self, message: tuple[tuple[str, int, tuple[int, int], int]]):
    
    i = 0
    while i < len(cities):
        city = cities[i]
        if city[2] == message[0][2]:
            cities.pop(i)
            i -= 1
        i += 1
    
    city = message[0]
    cities.append(city)

@mc.respond.event("GAME/UPDATE/TILE")
def update_tile(self, message: tuple[tuple[int, int, tuple[int, int], int, int]]):
    world[message[0][2][1]][message[0][2][0]] = (message[0][0], message[0][3], message[0][4])

@mc.respond.event("GAME/UPDATE/TECH")
def update_tech(self, message: tuple[int]):
    print(f"techs = {message[0]}")

def console(name):
    a = input("> ")
    if a == "readiness":
        print(readiness)
    elif a == "names":
        print(names)
    elif a == "admin":
        password = input("input password: ")
        mc.send(Format.event("LOBBY/ADMIN", [password]))
    elif a == "ready":
        mc.send(Format.event("LOBBY/READY", [1]))
        readiness[name] = 1
    elif a == "not ready":
        mc.send(Format.event("LOBBY/READY", [1]))
        readiness[name] = 0
    elif a == "say":
        message = input("> ... ")
        mc.send(Format.event("MESSAGE", [message]))
    elif a == "world":
        mc.send(Format.request("GAME/WORLD", []))
    elif a == "mov":
        pos1 = tuple(map(int, input("> ... ").split("/")))
        pos2 = tuple(map(int, input("> ... ").split("/")))
        print(Format.event("GAME/MOVE_UNIT", [pos1, pos2]))
        mc.send(Format.event("GAME/MOVE_UNIT", [pos1, pos2]))
    elif a == "units":
        mc.send(Format.request("GAME/UNITS", []))
    elif a == "cities":
        mc.send(Format.request("GAME/CITIES", []))
    elif a == "end":
        print(Format.event("GAME/END_TURN", []))
        mc.send(Format.event("GAME/END_TURN", []))
    elif a == "req" or a == "request":
        route = input("> route: ")
        mc.send(Format.request(route, []))
    elif a == "eve" or a == "event":
        route = input("> route: ")
        mc.send(Format.event(route, []))
    elif a == "inf" or a == "info" or a == "inform":
        route = input("> route: ")
        mc.send(Format.info(route, []))
    elif a == "err" or a == "error":
        route = input("> route: ")
        mc.send(Format.error(route, []))
    else:
        print("UNKNOWN COMMAND")

@mc.set_main_cycle
def main_cycle():
    global screen
    name = input("print your nickname: ")
    mc.send(Format.event("LOBBY/JOIN", [name]))

    mc.send(Format.request("LOBBY/NAMES", []))
    mc.send(Format.request("LOBBY/READINESS", []))

    pg.init()
    colors_for_tiles = (
        (0, 0, 200),
        (100, 100, 250),
        (100, 250, 100),
        (0, 200, 0),
        (120, 120, 120),
    )
    colors_for_resources = (
        (200, 100, 100),
        (50, 150, 50),
        (150, 150, 250),
        (200, 200, 50),
        (100, 50, 50),
    )
    colors_for_buildings = (
        (100, 50, 50),
        (200, 200, 50),
    )
    colors_for_cities = (
        (200, 10, 10), 
        (10, 200, 10), 
        (10, 10, 200), 
        (200, 200, 10),
    )
    colors_for_units = (
        (200, 100, 100), 
        (100, 200, 100), 
        (100, 100, 200), 
        (200, 200, 100), 
    )
    selected = None
    while True:
        if not game_started :
            console(name)
        else:
            if screen is None:
                screen = pg.display.set_mode((900, 900))
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    mc.sock.close()
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        mc.send(Format.request("GAME/UNITS", []))
                        mc.send(Format.request("GAME/CITIES", []))
                        mc.send(Format.request("GAME/WORLD", []))
                    if event.key == pg.K_SPACE:
                        mc.send(Format.event("GAME/END_TURN", []))
                    if event.key == pg.K_e:
                        mc.send(Format.event("GAME/CREATE_UNIT", [selected, 0]))
                    if event.key == pg.K_r:
                        mc.send(Format.event("GAME/CONQUER_CITY", [selected]))
                    if event.key == pg.K_t:
                        mc.send(Format.event("GAME/HARVEST", [selected]))
                    if event.key == pg.K_f:
                        mc.send(Format.event("GAME/BUILD", [selected, 0]))
                    if event.key == pg.K_0:
                        mc.send(Format.event("GAME/BUY_TECH", [0]))
                    if event.key == pg.K_1:
                        mc.send(Format.event("GAME/BUY_TECH", [1]))
                    if event.key == pg.K_2:
                        mc.send(Format.event("GAME/BUY_TECH", [2]))

                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        selected = (event.pos[0] // 50, event.pos[1] // 50)
                        print(f"SELECTED = {selected}")
                    elif event.button == 3:
                        target = (event.pos[0] // 50, event.pos[1] // 50)
                        print(f"TARGET = {target}")
                        mc.send(Format.event("GAME/MOVE_UNIT", [selected, target]))
                        print(units)
            
            screen.fill((0, 0, 0))
            for x in range(18):
                for y in range(18):
                    if world[y][x]:
                        pg.draw.rect(screen, colors_for_tiles[world[y][x][0]], (x * 50, y * 50, 50, 50))
                        if world[y][x][1] != -1:
                            pg.draw.circle(screen, colors_for_resources[world[y][x][1]], ((x + 0.5) * 50, (y + 0.5) * 50), 15)
                        if world[y][x][2] != -1:
                            pg.draw.rect(screen, colors_for_buildings[world[y][x][2]], (x * 50 + 10, y * 50 + 10, 30, 30))
            for city in cities:
                pg.draw.circle(screen, colors_for_cities[city[1]], ((city[2][0] + 0.5) * 50, (city[2][1] + 0.5) * 50), 20)

            for unit in units:
                pg.draw.circle(screen, colors_for_units[unit[1]], ((unit[2][0] + 0.5) * 50, (unit[2][1] + 0.5) * 50), 17)

            pg.display.flip()

IPaddr = input("print Ipv4: ")

mc.init_client((IPaddr, 9090))
mc.start()



"""
default commands:

26.220.113.32
antiantilopa
admin
a
ready

req
GAME/UNITS

req
GAME/VISION

"""