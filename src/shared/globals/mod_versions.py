
from typing import Annotated
from netio import Serializable, SerializeField


class ModConfig(Serializable):
    name: Annotated[str, SerializeField()]
    version: Annotated[str, SerializeField()]

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    def to_serializable(self):
        return [self.name, self.version]

    def from_serializable(data: tuple[str, str]) -> "ModConfig":
        return ModConfig(name=data[0], version=data[1])

    def __eq__(self, value: "ModConfig"):
        return (self.name == value.name) and (self.version == value.version)

    def __ne__(self, value: "ModConfig"):
        return (self.name != value.name) or (self.version != value.version)

class ModVersions:
    mods: list[ModConfig] = []