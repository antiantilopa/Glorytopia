import json, os, datetime
from pathlib import Path

class ChosenVar:
    variants: list
    chosen: int

    def __init__(self, variants: list, chosen: int):
        self.variants = variants
        self.chosen = chosen

class OrderVar:
    order: list

    def __init__(self, order: list):
        self.order = order

class InputVar:
    var: str

    def __init__(self, var: str):
        self.var = var

class IntVar:
    value: int

    def __init__(self, value: int):
        self.value = value

class RecordReplaySettings:
    record_replay: ChosenVar = ChosenVar([0, 1], 1)
    replay_file_name: str = str(datetime.datetime.now()).split(".")[0].replace(":", "-")
    replay_path = Path("../replays/")

    @staticmethod
    def save_to_file_():
        new_settings = {
            "record_replay": RecordReplaySettings.record_replay.variants[RecordReplaySettings.record_replay.chosen],
        }
        
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "record_settings.json"), "w") as f:
            json.dump(new_settings, f, indent=2)
    
    @staticmethod
    def get_from_file_():
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "record_settings.json"), "r") as f:
            settings_json = json.load(f)
        RecordReplaySettings.record_replay.variants[RecordReplaySettings.record_replay.chosen] = settings_json.get("record_replay", 0)