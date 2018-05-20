# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 12:35
'''
from cocos.layer import Layer
from .text import layout
from .info import Info

class Loading(Layer):
    def __init__(self):
        super(Loading, self).__init__()
        inf = Info((640,480), center=True)
        self.add(inf)
        inf.display(['hello, world'])



if __name__ == '__main__':
    from cocos.director import director
    from cocos.scene import Scene
    director.init(width=800, height=600)
    director.run(Scene(Loading()))
