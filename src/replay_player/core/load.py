import os
from pathlib import Path
from server.core.ability import Ability
from server.core.game import Game
from server.globals.replay import RecordReplaySettings
from serializator.net import *
from server.globals.mod_versions import ModVersions, ModConfig
from shared import *
from shared.loader import load_mains
from .frame import Frame
from .replay import Replay

def load(path: str|Path) -> tuple[Game, list[Frame]]:
    load_mains()
    full_path = RecordReplaySettings.replay_path / path
    if not os.path.exists(full_path):
        raise FileNotFoundError(full_path)
    with open(full_path, "rb") as f:
        data = f.read()
    data = SerializationTypes.LIST_BEGIN.to_bytes() + data + SerializationTypes.END.to_bytes()
    try:
        data = Serializator.decode_full(data)
        print("    ============ decoded normally!!!")
        mods_data = data[0]
        mods: list[ModConfig] = list(map(ModConfig.from_serializable, mods_data))

        if len(mods) != len(ModVersions.mods):
            error_message = "mods number are not the same as in replay.\nreplay uses next mods:"
            for mod in mods:
                error_message += f"\n{mod.name}: {mod.version}"
            raise Exception(error_message)
        for i in range(len(mods)):
            if ModVersions.mods[i] not in mods:
                raise Exception(f"the mod {ModVersions.mods[i]} is not used in the replay")

        game_data = data[1]
        game = Game.from_serializable(game_data)
        frames_data = data[2:]
        frames = [Frame(i[0], i[1], i[2], i[3]) for i in frames_data]
        return Replay(game, game_data, frames)
        
    except:
        raise Exception(f"cant decode the replay: {full_path}")
    