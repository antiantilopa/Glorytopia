from pygame_tools_tafh import *

from client.components.widgets import LabelComponent, RectButtonComponent

from .epilog_scene import TestEpilogScene


class MenuScene(Scene):

    def load(self, data):
        title = "Glorytopia"
        color = (255, 50, 50)

        label = GameObject("label")
        label.add_component(LabelComponent(title, color))
        label.transform.position = Vector2d(400, 300)
        scale = label.get_component(LabelComponent).scale_x = 5

        button = GameObject("button")
        button.add_component(
            RectButtonComponent(lambda *args: (self.destroy(), TestEpilogScene().load()), Vector2d(100, 50)))
        button.add_component(LabelComponent("Play", color))
        button.transform.position = Vector2d(400, 400)

        twn = Tweens()

        twn.add(label.get_component(LabelComponent), "scale_x", scale, 1, -1, 1, 0)
        twn.add(label.get_component(LabelComponent), "scale_y", scale, 1, -1, 1, 0)
        twn.add(label.transform.position, "y", label.transform.position.y, 100, -1, 5, 2)

        twn.add(button.get_component(LabelComponent), "scale_x", scale, 1, -1, 1, 0)
        twn.add(button.get_component(LabelComponent), "scale_y", scale, 1, -1, 1, 0)
        twn.add(button.transform.position, "y", button.transform.position.y, 200, -1, 5, 2)