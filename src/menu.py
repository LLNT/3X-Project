# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.layer import ColorLayer

class Menu(ColorLayer):
    is_event_handler = True
    def __init__(self,w,h):
        super(Menu, self).__init__(0, 0, 0, 0, width=100, height=400)
        self.position = w/2, h/2

    def on_mouse_press(self, x, y, buttons, modifiers):
        print(1)