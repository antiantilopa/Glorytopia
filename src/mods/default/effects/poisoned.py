from shared.effect import Effect
from server.core.unit import Unit

class Poisoned(Effect):
    name = "poisoned"
    dmg: int
    increase: int
    stackable = False
    
    def __init__(self, duration=-1, base_dmg=1, increase=0):
        self.dmg = base_dmg
        super().__init__(duration)
    
    def on_end_turn(self, unit):
        unit.health -= self.dmg
        self.dmg += self.increase