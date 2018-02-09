# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/9 22:43
'''
from cocos.layer import ColorLayer
from cocos.actions import IntervalAction
class Scale_to(IntervalAction):
    def init(self, scale_x, scale_y, duration=5):
        self.end_scale_x = scale_x
        self.end_scale_y = scale_y
        self.duration = duration

    def start(self):
        self.start_scale_x = self.target.scale_x
        self.start_scale_y = self.target.scale_y
        self.delta_x = self.end_scale_x - self.start_scale_x
        self.delta_y = self.end_scale_y - self.start_scale_y

    def update(self, t):
        self.target.scale_x = self.start_scale_x + self.delta_x * t
        self.target.scale_y = self.start_scale_y + self.delta_y * t

class Bar(ColorLayer):
    def __init__(self, **kwargs):
        if 'color' in kwargs:
            r,g,b = kwargs['color']
        else:
            r,g,b = (0, 0, 0)
        if 'alpha' in kwargs:
            a = kwargs['alpha']
        else:
            a = 255
        w, h = kwargs['size']
        super().__init__(r,g,b,a,w,h)
        self.scale_x = kwargs['prop']
        self.position = kwargs['position']
        self.anchor = (0, 0)