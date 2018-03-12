# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/7 11:29
'''
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.scene import Scene

class Background(Layer):
    def __init__(self, window_size, pic):
        super().__init__()
        map = Sprite(pic)
        w, h = window_size
        # map.scale_x, map.scale_y = w/map.width, h/map.height
        map.image_anchor = (0, 0)
        # map.position = map.width//2, map.height//2
        self.add(map)

if __name__ == '__main__':
    from cocos.director import director
    import pyglet
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init()
    director.run(Scene(Background(640,480)))
    pass