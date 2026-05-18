from shared.effect import EffectType, Effect
from server.core.unit import Unit

class Poisoned(EffectType):
    name = "poisoned"
    stackable = False
    
    @staticmethod
    def on_end_turn(effect: Effect, unit):
        if effect.duration == 0:
            return
        dmg, increase = effect.args[0], effect.args[1]
        unit.health -= dmg
        effect.args[0] += increase