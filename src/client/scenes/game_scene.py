from pygame_tools_tafh import GameObject, Scene, SpriteComponent, Vector2d


class GameScene(Scene):

    def load(self):
        SpriteComponent.set_path("src/client/assets/textures/new")
        sprite = SpriteComponent("tile.png", (256, 256))
        world = GameObject("tile")
        world.add_component(sprite)
        world.transform.position = Vector2d(100, 100)