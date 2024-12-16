from pygame_tools_tafh import GameObject, Scene, SpriteComponent, Vector2d


class GameScene(Scene):

    def load(self):
        tile = GameObject("tile")
        tile.add_component(SpriteComponent("tile.png", (32, 32)))
        tile.transform.position = Vector2d(100, 100)