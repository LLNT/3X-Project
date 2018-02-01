# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:03
'''
from cocos.sprite import Sprite

class Mapcell(Sprite):
    def __init__(self, size=50,pos=None,state='none',path='ring.png',color=(255, 255, 255)):
        super(Mapcell, self).__init__(image=path)
        self.scale = size/self.height
        self.color = color
        self.position = pos
        self.state = state