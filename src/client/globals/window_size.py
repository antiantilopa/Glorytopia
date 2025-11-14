from engine_antiantilopa import Vector2d

class WindowSize:
    value: Vector2d = Vector2d(1200, 800)

    _block_size: Vector2d = Vector2d(100, 100)

    @staticmethod
    def get_block_size() -> Vector2d:
        return WindowSize._block_size * WindowSize.value / Vector2d(1200, 800)