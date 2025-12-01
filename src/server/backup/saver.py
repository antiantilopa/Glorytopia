import os
from pathlib import Path

from netio.serialization.serializer import SerializationTypes
from server.core.city import City
from server.core.game import Game
from server.core.unit import Unit
from shared.player import PlayerData_
from server.core.player import Player
from shared.globals.mod_versions import ModVersions
from server.globals.backup import BackupSettings
from netio import BaseWriter

def to_bytes(obj) -> bytes:
    return Saver.writer._any_to_bytes(obj)

class Saver:
    writer = BaseWriter()

    @staticmethod
    def save_current_state() -> None:
        if BackupSettings.backup_number.value == 0:
            return
        if not os.path.exists(BackupSettings.saves_path):
            os.mkdir(BackupSettings.saves_path)
        if not os.path.exists(BackupSettings.saves_path / f"{BackupSettings.save_folder_name}"):
            os.mkdir(BackupSettings.saves_path / f"{BackupSettings.save_folder_name}")

        with open(Saver.get_save_file_path(), "wb") as f:
            f.write(bytes([SerializationTypes.LIST.value]))
        Saver.record_mods()
        Saver.record_game_data()
        Saver.record_player_datas([p.pdata for p in Player.players])
        Saver.record_world()
        Saver.record_objects()
        Saver.record_players(Player.players)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(bytes([SerializationTypes.END_OF_OBJECT.value]))
        Saver.delete_old_backups()

    @staticmethod
    def delete_old_backups() -> None:
        saves_folder = BackupSettings.saves_path / f"{BackupSettings.save_folder_name}"
        saves = os.listdir(saves_folder)
        if len(saves) > BackupSettings.backup_number.value:
            saves.sort()
            num_to_delete = len(saves) - BackupSettings.backup_number.value
            for i in range(num_to_delete):
                os.remove(saves_folder / saves[i])

    @staticmethod
    def record_mods():
        data = to_bytes(ModVersions.mods)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data)

    @staticmethod
    def record_player_datas(player_datas: list[PlayerData_]):
        data = to_bytes(player_datas)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data)

    @staticmethod
    def record_players(players: list[Player]):
        player_datas = []
        for player in players:
            flat_vision = [item for sublist in player.vision for item in sublist]
            player_datas.append((player.id, player.money, player.techs, list_bool_to_list_int32(flat_vision)))
        data = to_bytes(player_datas)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data)

    @staticmethod
    def record_game_data():
        game = Game.obj
        game_data = (game.world.size, len(game.players), game.now_playing_player_index, game.turn_number)
        data = to_bytes(game_data)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data)

    @staticmethod
    def record_world():
        # HACK wtf r ya doin? can save a buncha memory! 
        # essentially, it is because every tile has its position stored. 
        world_data = []
        for row in Game.obj.world.world:
             for tile in row:
                world_data.append(tile)
        data = to_bytes(world_data)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data)
    
    @staticmethod
    def record_objects():
        units = Unit.units
        cities = City.cities
        data1 = to_bytes(units)
        data2 = to_bytes(cities)
        with open(Saver.get_save_file_path(), "ab") as f:
            f.write(data1)
            f.write(data2)

    @staticmethod
    def get_save_file_path() -> Path:
        return BackupSettings.saves_path / f"{BackupSettings.save_folder_name}" / f"turn{Game.obj.turn_number}-{Game.obj.now_playing_player_index}.save"

def list_bool_to_list_int32(x: list[bool]) -> list[int]:
    result = []
    for i in range(len(x) // 32 + (1 if len(x) % 32 else 0)):
        num = 0
        for j in range(32):
            if 32 * i + j >= len(x):
                break
            num += x[32 * i + j] * (2 **(31 - j))
        result.append(num)
    return result

