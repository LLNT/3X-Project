# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/7 11:29
'''
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.scene import Scene

class Background(Layer):
    def __init__(self, w, h):
        super().__init__()
        map = Sprite('map0_temp.jpg')
        map.scale_x, map.scale_y = w/map.width, h/map.height
        map.position = w//2, h//2
        self.add(map)

if __name__ == '__main__':
    from cocos.director import director
    import pyglet
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init()
    director.run(Scene(Background(640,480)))
    pass