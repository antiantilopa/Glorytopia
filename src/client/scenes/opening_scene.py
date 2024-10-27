from pygame_tools_tafh import *

from client.components.label import LabelComponent


class OpeningScene(Scene):
    
    def load(self):
        title = "Glorytopia"
        color = (255, 50, 50)

        label = GameObject("label")
        label.add_component(LabelComponent(title, color))
        label.transform.position = Vector2d(400, 300)
        scale = label.get_component(LabelComponent).scale_x = 5
        twn = Tweens()

        twn.add(label.get_component(LabelComponent), "scale_x", scale, 1, -1, 1, 0)
        twn.add(label.get_component(LabelComponent), "scale_y", scale, 1, -1, 1, 0)
