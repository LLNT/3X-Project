# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer

class Battle(ColorLayer):
    is_event_handler = True
    def __init__(self, w=800, h=600):
        super(Battle, self).__init__(0,0,0,0,width=w, height=h)


    def on_mouse_press(self, x, y, buttons, modifiers):
        director.pop()

