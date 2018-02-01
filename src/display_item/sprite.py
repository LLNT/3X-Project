# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:03
'''
from cocos.sprite import Sprite
from person import Person

def coordinate(i, j, size):
    x = i * size + size // 2
    y = j * size + size // 2
    return x, y

def coordinate_t(x, y, size):
    i = x // size
    j = y // size
    return i, j

class Cell(Sprite):
    def __init__(self, size=50,pos=(0, 0),state='default',path='ring.png',color=(255, 255, 255)):
        '''

        :param size: fixed size of every cell's length and width
        :param pos:  position of the cell, should be transformed to the pixel position of left_down
        :param state:  record state includes default, with person on, target
        :param path: resource file path
        :param color:
        '''
        super(Cell, self).__init__(image=path)
        self.scale = size/self.height
        self.color = color
        self.position = coordinate(pos[0], pos[1], size)
        self.state = state

class Charactor(Sprite):
    def __init__(self, person, size=50,pos=(0, 0),state='default',path='ring.png',color=(255, 255, 255)):
        '''

        :param person: person object this sprite refers to
        :param size: fixed size of every cell's length and width
        :param pos:  position of the cell, should be transformed to the pixel position of left_down
        :param state:  record state includes default, with person on, target
        :param path: resource file path
        :param color:
        '''
        super(Charactor, self).__init__(image=path)
        self.scale = size/self.height
        self.color = color
        self.position = coordinate(pos[0], pos[1], size)
        self.state = state
        self.person = person        #type:Person
        self.pid = person.pid
        self.pos = pos


