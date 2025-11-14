import json, os

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

resolutions = [(1680, 1120), (1440, 960), (1200, 800), (960, 640), (720, 480), (600, 400)]

class Settings:
    resolution: ChosenVar = ChosenVar(resolutions, 2)
    pref_ipv4: InputVar = InputVar("")
    pref_name: InputVar = InputVar("")
    texture_packs: OrderVar = OrderVar(["default"])
    preffered_color: ChosenVar = ChosenVar([0, 1, 2, 3, 4, 5, 6, 7], 2)

    @staticmethod
    def save_to_file_():
        new_settings = {
            "resolution": Settings.resolution.variants[Settings.resolution.chosen],
            "preffered_ipv4": Settings.pref_ipv4.var,
            "preffered_name": Settings.pref_name.var,
            "texture_packs": Settings.texture_packs.order,
            "preffered_color": Settings.preffered_color.chosen
        }
        
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "settings.json"), "w") as f:
            json.dump(new_settings, f, indent=2)
        
        print("new settings saved")
    
    @staticmethod
    def get_from_file_():
        p = os.path.dirname(__file__)
        with open(os.path.join(p, "settings.json"), "r") as f:
            settings_json = json.load(f)
        Settings.resolution.chosen = resolutions.index(tuple(settings_json["resolution"]))
        Settings.pref_ipv4.var = settings_json["preffered_ipv4"]
        Settings.pref_name.var = settings_json["preffered_name"]
        Settings.texture_packs.order = settings_json["texture_packs"]
        Settings.preffered_color.chosen = settings_json["preffered_color"]

        for texture_pack in os.listdir("\\".join(p.split("\\")[:-1] + ["assets"])):
            if texture_pack not in Settings.texture_packs.order:
                Settings.texture_packs.order.append(texture_pack)