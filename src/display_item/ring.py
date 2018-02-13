# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/9 12:03
'''
from cocos.cocosnode import CocosNode
from cocos.actions import RotateTo, RotateBy, Delay, CallFunc
from cocos.sprite import Sprite
from display_item.text import Text
from utility import *
from cocos.director import director
class Ring(CocosNode):

    def __init__(self, position, scale, start_color=GREEN, end_color=RED,
                 prop=1, back_color = BLACK):
        super().__init__()
        self.start_color = start_color
        self.end_color = end_color
        self.delta = self._diff(self.end_color, self.start_color)
        self.position = position
        self.left_ring = Sprite(image='ring_right.png', color=start_color, position=(0, 0),
                                scale=scale, rotation=180)
        self.right_ring = Sprite(image='ring_right.png', position=(0, 0), scale=scale,
                                 color=start_color)
        self.mask_ring = Sprite(image='ring_right.png', position=(0, 0), scale=scale,
                                color=back_color)
        self.backend = Sprite(image='ring.png', color=back_color, position=(0, 0),
                                scale=scale)

        self.add(self.backend)
        self.add(self.left_ring)
        self.add(self.right_ring)
        self.add(self.mask_ring)
        self.right_ring.busy = False
        self.set_prop(prop)
        self.schedule(self.update)

    def set_prop(self, prop):
        angle = 360 - prop * 360
        self.angles = angle
        if angle > 180:
            self.mask_visible()
        else:
            self.left_visible()
        self.right_ring.rotation = angle

    def set_busy(self):
        self.right_ring.busy = False

    def set_angle_action(self, proportion, max_duration=4, min_duration=2):
        angle = 360 - proportion * 360
        delta = abs(self.angles - angle)
        if delta <= 10:
            return self.right_ring, Delay(min_duration)
        duration = min(1, delta / 90) * (max_duration - min_duration)
        if self.angles > angle: # right rotation
            if angle >= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(180, duration + min_duration) + CallFunc(self.change_angle, angle))
            elif self.angles <= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration + min_duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = (duration + min_duration) * (self.angles - 180) / delta
                d2 = duration + min_duration - d1
                return self.right_ring, (Delay(0.5) + RotateTo(180, d1)
                                   + RotateBy(angle - 180, d2) + CallFunc(self.change_angle, angle))
        else: #
            if angle <= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration + min_duration) + CallFunc(self.change_angle, angle))
            elif self.angles >= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration + min_duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = (duration + min_duration) * (180 - self.angles) / delta
                d2 = duration + min_duration - d1
                return self.right_ring, (Delay(0.5) + RotateBy(180 - self.angles, d1)
                                   + RotateBy(angle - 180, d2) + CallFunc(self.change_angle, angle))

    def update(self, dt):

        self.r = (self.right_ring.rotation) / 360
        if self.r == 0 and self.angles == 360:
            self.r = 1
        if self.r > 0.5:
            self.mask_visible()
        else :
            self.left_visible()
        color = [0, 0, 0]
        for i in range(3):
            color[i] = int(self.r * self.delta[i] + self.start_color[i])
        self.right_ring.color = color
        self.left_ring.color = color

    def _diff(self, color1, color2):
        color = [0, 0, 0]
        for i in range(3):
            color[i] = color1[i] - color2[i]
        return color

    def left_visible(self):
        self.left_ring.visible = True
        self.mask_ring.visible = False

    def mask_visible(self):
        self.left_ring.visible = False
        self.mask_ring.visible = True

    def change_angle(self, angle):
        self.angles = angle



class Scoreboard(Ring):
    def __init__(self, position, scale, start_color=GREEN, end_color=RED,
                 prop=1, back_color = BLACK, hp=20, mhp=20):
        super().__init__(position, scale, start_color=start_color, end_color=end_color,
                 prop=prop, back_color = back_color)
        self.hp = Text(str(hp), (0, 0), color=(255, 255, 255, 255))
        self.add(self.hp)
        self.mhp = mhp

    def update(self, dt):
        super().update(dt)
        self.hp.element.text = str(self.mhp - int(self.r * self.mhp))
        # self.hp.element.color = color[0], color[1], color[2], 255

class PerSpr(Ring):
    def __init__(self, person, scale=1,size=50,pos=(0, 0),controller=0,state='unmoved',
                 st_color=GREEN, ed_color=RED, bk_color=WHITE):

        position = coordinate(pos[0], pos[1], size)
        scl = scale * size / 400
        self.person = person
        super().__init__(position=position, scale=scl, start_color=st_color,
                         end_color=ed_color, back_color=bk_color)
        self.update_hp()
        self.controller = controller
        self.state = state
        self.pid = person.pid
        self.pos = pos
        self.inner = Sprite(image='ring.png', scale=scl*0.9)
        self.add(self.inner)

    def update_hp(self):
        self.hp = self.person.ability['HP']
        self.mhp = self.person.ability['MHP']
        self.set_prop(self.hp/self.mhp)
