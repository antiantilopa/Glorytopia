
import multiprocessing as mp
from typing import Any, Callable
from netio import sync_key

import server.core
from server.core.player import Player
from shared.asset_types import Nation, TechNode
from shared.city import CityData
from shared.error_codes import ErrorCode, ErrorCode
from shared.player import SharedPlayerData
from shared.tile import TileData
from shared.unit import UnitData
from shared.util.position import Pos

class Move:
    args: Any
    _func: Callable[[SharedPlayerData, Any], ErrorCode]

    def __init__(self, func: Callable[[SharedPlayerData, Any], ErrorCode], args: Any):
        self._func = func
        self.args = args

class DummyObj:
    pos: Pos
    cls: type

    def __init__(self, obj):
        if hasattr(obj, "pos"):
            self.pos = obj.pos
            self.cls = type(obj)
        else:
            raise ValueError(f"given obj {obj} does not have pos attribute")

class BotMemory:
    world: "server.core.world.World"

    def __init__(self):
        self.world = server.core.world.World.object

@sync_key("bot_data")
class BotData(SharedPlayerData):
    def __init__(self):
        self.id = -1

        self.color = 0
        self.recovery_code = 0
        self.joined = False
        self.is_ready = False
        self.nickname = ""
        self.nation = Nation.by_id(0)

def default_bot(bot: "Bot", queue: mp.Queue):
    import random
    server.core.world.World.object = bot.memory.world
    for row in bot.memory.world.unit_mask:
        for unit in row:
            if unit is not None:
                server.core.unit.Unit.units.append(unit)
    for row in bot.memory.world.city_mask:
        for city in row:
            if city is not None:
                server.core.city.City.cities.append(city)
    Player.players = [Player() for i in range(bot.id)]
    Player.players.append(bot)
    for unit in bot.units:
        attacks = unit.get_attacks()
        if len(attacks) != 0:
            queue.put(Move(Bot.move_unit, [DummyObj(unit), attacks[random.randint(0, len(attacks)-1)].pos]))
        else:
            moves = unit.get_movements()
            if len(moves) != 0:
                queue.put(Move(Bot.move_unit, [DummyObj(unit), moves[random.randint(0, len(moves)-1)][0]]))
    queue.put(None)

class Bot(Player):
    # bot should implement this method to return a list of moves
    # after it is called, the moves will be executed, and memory will be updated.
    # to end the turn, add None to the end of the list of moves.
    # Moves after None will be ignored.
    main_func: Callable[["Bot", mp.Queue], list[Move]]
    memory: BotMemory

    timeout_s: float = 30 # number of seconds for function call

    def __init__(self, new_player = True, nation = None):
        Player.__init__(self, new_player, nation)
        self.memory = BotMemory() 
        self.pdata = BotData()
        self.pdata.init()
        self.pdata.color = self.id % 8
        self.main_func = default_bot

    def get_moves(self) -> list[Move]:
        if self.main_func is None:
            return [None]
        queue = mp.Queue(1024)
        process = mp.Process(target=get, args=[self, queue])
        process.start()
        process.join(Bot.timeout_s)
        result = []
        while not queue.empty():
            move = queue.get()
            result.append(move)
        if process.is_alive():
            process.terminate()
            print("bot was taking too much time")
        # if len(result) == 0:
        #     result.append(None)
        return result
    
    def set_function(self, func: Callable[["Bot"], list[Move]]):
        self.main_func = func
    
    def execute_moves(self, moves: list[Move], player_data: SharedPlayerData) -> bool:
        for move in moves:
            if move is None:
                return True
            for i in range(len(move.args)):
                arg = move.args[i]
                if not isinstance(arg, DummyObj):
                    continue
                if issubclass(arg.cls, UnitData):
                    move.args[i] = server.core.world.World.object.get_unit(arg.pos)
                if issubclass(arg.cls, CityData):
                    move.args[i] = server.core.world.World.object.get_city(arg.pos)
                if issubclass(arg.cls, TileData):
                    move.args[i] = server.core.world.World.object.get(arg.pos)
            error_code = move._func(player_data, *move.args)
            if error_code != ErrorCode.SUCCESS:
                print(f"Error executing move: {error_code.name}")
                return True
            
        return False

def get(bot: Bot, queue: mp.Queue):
    return bot.main_func(bot, queue)