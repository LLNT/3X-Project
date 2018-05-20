"""
@version: ??
@author: Antastsy
@time: 2018/3/4 22:06
"""
import pyglet
from cocos.director import director
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out
from cocos.scene import Scene
from cocos.layer import Layer
from src.display_item.arena import new_game, load_game, map_init
from src.display_item.saveload import Main as Saveload

class Main(Menu):

    def __init__(self, map,layer):
        super().__init__()
        self.map = map

        l = []
        l.append(MenuItem('New_game', self.new_game))
        l.append(MenuItem('Load_game', self.load_game,layer))
        l.append(MenuItem('Quit', self.quit))

        self.create_menu(l, zoom_in(), zoom_out())

    def new_game(self):
        new_game(self.map)

    def load_game(self):
        sl = Saveload(1280,720,None,'load')
        layer.add(sl)
        self.kill()

    def quit(self):
        director.pop()


if __name__ == '__main__':
    pyglet.resource.path = ['./img']
    pyglet.resource.reindex()
    director.init(caption='The Lost Books', width=1280, height=720)
    director.show_FPS = True
    img=pyglet.resource.image('cursor/sword.png',flip_x=True)
    img.width,img.height=40,40
    img.anchor_x,img.anchor_y=20,20
    cursor=pyglet.window.ImageMouseCursor(img)
    director.window.set_mouse_cursor(cursor)
    layer=Layer()
    director.run(Scene(layer,Main(map_init(),layer=layer)))
