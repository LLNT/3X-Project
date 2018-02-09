# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/8 22:09
'''
from cocos.batch import BatchableNode
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.scene import Scene
from display_item.battle_scene import Ring
import pyglet
from cocos.director import director
class PerSpr(Ring):
    def __init__(self, person, scale=1,size=50,pos=(0, 0),controller=0,state='unmoved',color=(255, 255, 255)):

        position = coordinate(pos[0], pos[1], size)
        scl = scale * size / 400
        self.person = person
        self.hp = person.ability['HP']
        self.mhp = person.ability['MHP']
        super().__init__(position=position, scale=scl,prop=self.hp/self.mhp)
        self.controller = controller
        self.state = state

        self.pid = person.pid
        self.pos = pos


class testlayer(Layer):
    def __init__(self):
        size = 80
        super().__init__()
        for i in range(5):
            for j in range(5):
                self.add(Ring(position=coordinate(i, j, size), scale=size / 400))

def coordinate(i, j, size):
    x = i * size + size // 2
    y = j * size + size // 2
    return x, y

if __name__ == '__main__':
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init(caption='3X-Project')
    director.run(Scene(testlayer()))

    pass