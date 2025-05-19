from client.scenes.main_menu import launch
from client.respondings import lobby, client, gameevents, gameinfo

c = client.Client()
c.respond.merge(lobby.respond)
c.respond.merge(gameevents.respond)
c.respond.merge(gameinfo.respond)

launch()