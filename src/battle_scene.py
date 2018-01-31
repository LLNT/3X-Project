# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer
from cocos.scenes import ShuffleTransition
from cocos.scene import Scene
from cocos.actions import CallFunc, Delay

class Battle(ColorLayer):
    is_event_handler = True
    def __init__(self, w=800, h=600):
        super(Battle, self).__init__(0,200,0,200,width=w, height=h)
        self.w = w
        self.h = h

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.do(CallFunc(self._return_arena)+ Delay(1) + CallFunc(self._pop))

    def _return_arena(self):
        director.push(ShuffleTransition(Scene(ColorLayer(0, 0, 0, 0, self.w, self.h)), duration=1.5))

    def _pop(self):
        director.pop()
        director.pop()