from server.core.ability import Ability
from server.core.world import World
from server.core.city import City
from server.core.unit import Unit
from server.core.tile import Tile
from shared.effect import Effect, EffectType

class Poisoning(Ability):
    name = "poisoning"

    @staticmethod
    def after_attack(unit, other):
        other.add_effect(Effect(EffectType.get("poisoned"), 5, [1, 0]))
