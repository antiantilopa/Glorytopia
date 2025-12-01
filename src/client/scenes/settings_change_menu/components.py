from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *
from typing import Any

class SettingVariableComponent(Component):
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value
        Component.__init__(self)

class ChooseComponent(SettingVariableComponent):
    variants: list
    chosen: int

    def __init__(self, variants: list, chosen: int, name: str):
        self.variants = variants
        self.chosen = chosen 
        SettingVariableComponent.__init__(self, name, chosen)

class OrderComponent(SettingVariableComponent):
    order: list

    def __init__(self, order: list, name: str):
        self.order = order
        SettingVariableComponent.__init__(self, name, order)

class InputComponent(SettingVariableComponent):
    var: str

    def __init__(self, var: str, name: str):
        self.var = var
        SettingVariableComponent.__init__(self, name, var)