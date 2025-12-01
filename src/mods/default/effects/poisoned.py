from shared.effect import EffectType, Effect
from server.core.unit import Unit

class Poisoned(EffectType):
    name = "poisoned"
    stackable = False
    
    def on_end_turn(effect: Effect, unit):
        dmg, increase = effect.args
        unit.health -= dmg
        effect.args[0] += increase