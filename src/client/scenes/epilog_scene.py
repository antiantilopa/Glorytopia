from pygame_tools_tafh import *
from pygame_tools_tafh import LabelComponent

class TestEpilogScene(Scene):

    def load(self, data):

        star_text = """
        Turmoil has engulfed the
        Galactic Republic. The taxation
        of trade routes to outlying star
        systems is in dispute.
        
        Hoping to resolve the matter
        with a blockade of deadly
        battleships, the greedy Trade
        Federation has stopped all
        shipping to the small planet
        of Naboo.
        
        While the Congress of the
        Republic endlessly debates
        this alarming chain of events,
        the Supreme Chancellor has
        secretly dispatched two Jedi
        Knights, the guardians of
        peace and justice in the
        galaxy, to settle the conflict....
        """

        cnt = 0
        for txt in star_text.split("\n"):
            label = GameObject("label")
            label.add_component(LabelComponent(txt, (255, 50, 50)))
            label.transform.position = Vector2d(400, 300 + cnt * 50)
            scale = label.get_component(LabelComponent).scale_x = 2
            twn = Tweens()
            twn.add(label.transform.position, "y", 300 + cnt * 50, -1000 + cnt * 50, 0, 20, 0)

            class ScaleManagerComponent(Component):
                
                def __init__(self):
                    self.enabled = False

                def update(self):
                    if (self.game_object.transform.position.y < 650 and not self.enabled):
                        twn.add(self.game_object.get_component(LabelComponent), "scale_x", scale, 0.5, 0, 2, 0)
                        twn.add(self.game_object.get_component(LabelComponent), "scale_y", scale, 0.5, 0, 2, 0)
                        self.enabled = True

            label.add_component(ScaleManagerComponent())
            cnt += 1

