import json, os, datetime

from anyio import Path

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

class BackupSettings:
    backup_number: IntVar = IntVar(5)
    save_folder_name: str = str(datetime.datetime.now()).split(".")[0].replace(":", "-")
    saves_path = Path("../saves/")

    @staticmethod
    def save_to_file_():
        new_settings = {
            "backup_number": BackupSettings.backup_number.value
        }
        
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "settings.json"), "w") as f:
            json.dump(new_settings, f, indent=2)
    
    @staticmethod
    def get_from_file_():
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "settings.json"), "r") as f:
            settings_json = json.load(f)
        BackupSettings.backup_number.value = settings_json.get("backup_number", 5)