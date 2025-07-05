from client.scenes.main_menu import launch
from client.respondings import lobby, client, gameevents, gameinfo
from engine_antiantilopa import Vector2d
import pygame as pg

c = client.Client()
c.respond.merge(lobby.respond)
c.respond.merge(gameevents.respond)
c.respond.merge(gameinfo.respond)

resolutions = [
    (1680, 1120),
    (1440, 960),
    (1200, 800),
    (960, 640),
    (720, 480),
    (600, 400),
]

for res in resolutions:
    if res[0] < pg.display.Info().current_w and res[1] < pg.display.Info().current_h:
        print(res)
        launch(Vector2d.from_tuple(res))
        break

client.Client.object.sock.close()