from engine_antiantilopa import *
from client.widgets.fastgameobjectcreator import *

def load(screen_size: Vector2d = Vector2d(1200, 800)):
    scene = create_game_object(tags="default_scene", size=screen_size)
    scene.disable()

    return scene

def launch(screen_size: Vector2d = Vector2d(1200, 800)):
    load(screen_size)
    scene = GameObject.get_game_object_by_tags("default_scene")

    e = Engine(screen_size)
    scene.enable()
    e.run()

if __name__ == "__main__":
    launch()