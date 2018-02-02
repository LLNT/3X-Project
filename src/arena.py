# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:02
'''
from cocos.layer import Layer
from cocos.director import director
from display_item.sprite import Charactor, Cell

class Arena(Layer):
    # the holder of map and roles
    is_event_handler = True

    def __init__(self, map):
        super(Arena, self).__init__()
        # initilize the holder according to the map

    def _repaint(self):
        # according to the state of every sprite within, repaint them in the correct color
        pass

    def on_mouse_motion(self, x, y, buttons, modifiers):
        # use _repaint
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        # according to the state link to correct function
        pass

    def _reset(self):
        # reset to initial state
        pass

    pass

class State():
    # control the event state
    def __init__(self, arena):
        self.arena = arena




if __name__ == '__main__':
    pass