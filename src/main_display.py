"""
@version: ??
@author: Antastsy
@time: 2018/3/4 22:06
"""
import pyglet
from cocos.director import director
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out
from cocos.scene import Scene
from display_item.arena import new_game, load_game, map_init

class Main(Menu):

    def __init__(self, map):
        super().__init__()
        self.map = map

        l = []
        l.append(MenuItem('New_game', self.new_game))
        l.append(MenuItem('Load_game', self.load_game))
        l.append(MenuItem('Quit', self.quit))

        self.create_menu(l, zoom_in(), zoom_out())

    def new_game(self):
        new_game(self.map)

    def load_game(self):
        map = self.map.map_load()[0]
        load_game(map)

    def quit(self):
        director.pop()


if __name__ == '__main__':
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init(caption='3X-Project', width=1280, height=720)
    director.run(Scene(Main(map_init())))