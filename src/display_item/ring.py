# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/9 12:03
'''
from cocos.batch import BatchableNode
from cocos.actions import RotateTo, RotateBy, Delay, CallFunc
from cocos.sprite import Sprite
from display_item.text import Text
from utility import *
from cocos.director import director
from display_item.action_control import Sequencial
import pyglet

class Ring(BatchableNode):

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
        self.hp = Text(text=str(hp), position=(0, 0), color=(255, 255, 255, 255),  font_size=30)
        self.add(self.hp)
        self.mhp = mhp

    def update(self, dt):
        super().update(dt)
        self.hp.element.text = str(self.mhp - int(self.r * self.mhp))
        # self.hp.element.color = color[0], color[1], color[2], 255

class Blood(BatchableNode):
    def __init__(self, size=80):
        super().__init__()
        self.blood_right = Sprite('sprite/Blood_r.png', anchor=(0, size/2))
        self.blood_left = Sprite('sprite/Blood_l.png', anchor=(size/2, size/2))
        self.left = Sprite('sprite/Left.png', anchor=(size/2, size/2))
        self.right = Sprite('sprite/Right.png', anchor=(0, size/2))

        self.add(self.blood_right)
        self.add(self.left)
        self.add(self.blood_left)
        self.add(self.right)
        self.right.visible = False


    def set_visible(self, right=True):
        self.right.visible = right

    def set_prop(self, prop):
        self.prop = prop

    def set_angle(self, prop):
        self.prop = prop
        if self.prop <=0.5:
            self.set_visible(True)
            self.right.rotation = (0.5 - self.prop) * 360
            self.left.rotation = 180
        else:
            self.set_visible(False)
            self.right.rotation = 0
            self.left.rotation = (1 - self.prop) * 360

    def set_angle_action(self, prop, max_duration=4, min_duration=2):
        delta = abs(self.prop - prop)
        angle = delta * 360
        duration = min(1, delta * 4) * (max_duration - min_duration) + min_duration
        if prop > self.prop:
            # a right rotation, blood will be more
            if self.prop > 0.5:
                return Sequencial([
                    (self.left,  reversed(RotateBy(angle, duration)))
                ])
            elif prop <= 0.5:
                return Sequencial([
                    (self.right, reversed(RotateBy(angle, duration)))
                ])
            else:
                _angle = (0.5 - self.prop)*360
                _duration = _angle/angle * duration
                return Sequencial([
                    (self.right, reversed(RotateBy(_angle, _duration))),
                    (self.right, CallFunc(self.set_visible, False)),
                    (self.left, reversed(RotateBy(angle - _angle, duration - _duration)))
                ])
        else:
            if self.prop <= 0.5:
                return Sequencial([
                    (self.left,  RotateBy(angle, duration))
                ])
            elif prop > 0.5:
                return Sequencial([
                    (self.right, RotateBy(angle, duration))
                ])
            else:
                _angle = (self.prop - 0.5)*360
                _duration = _angle/angle * duration
                return Sequencial([
                    (self.left, RotateBy(_angle, _duration)),
                    (self.right, CallFunc(self.set_visible, True)),
                    (self.right, RotateBy(angle - _angle, duration - _duration))
                ])
            pass
        pass


class PerSpr(BatchableNode):
    def __init__(self, person, scale=1,size=50,pos=(0, 0),controller=0,state='unmoved'):
        position = coordinate(pos[0], pos[1], size)
        scl = scale * size / 400
        name = 'cls/' + person.cls + '_' + str(controller) + '.png'
        self.blood = Blood()
        self.size = size
        self.icon = Sprite(image=person.icon, position=(size//2-14, -size//2+14))
        super().__init__()
        try:
            self.img = Sprite(image=name)

        except:
            self.img = Sprite(image='sprite/Blood.png')
        self.img.scale_y, self.img.scale_x = size / self.img.height, size / self.img.width

        self.add(self.img, z=0)
        self.add(self.blood, z=1)
        self.add(self.icon, z=2)
        self.position = position
        self.person = person
        self.update_hp()
        self.controller = controller
        self.state = state
        self.moved = False
        self.pid = person.pid
        self.pos = pos
        self.icon.scale_x, self.icon.scale_y = 28 / self.icon.width , 28 / self.icon.height

    def _set_scale(self, s):
        super()._set_scale(s)
        self.blood.blood_right.scale = s
        self.blood.blood_left.scale = s
        self.blood.left.scale = s
        self.blood.right.scale = s
        self.icon.scale = s
        self.img.scale = s*0.9

    def _set_position(self, pos):
        super()._set_position(pos)
        self.blood.blood_right.position = pos
        self.blood.blood_left.position = pos
        self.blood.left.position = pos
        self.blood.right.position = pos
        self.icon.position = (pos[0] + self.size//2-14, pos[1]-self.size//2+14)
        self.img.position = pos

    def update_hp(self, set=True):
        self.hp = self.person.ability['HP']
        self.mhp = self.person.ability['MHP']
        prop = self.hp/self.mhp
        if set:
            self.blood.set_angle(prop)
        else:
            return prop

if __name__ == '__main__':
    pyglet.resource.path = ['../../img']
    pyglet.resource.reindex()
    director.init()
    import cocos
    layer = cocos.layer.Layer()
    batch = cocos.batch.BatchNode()
    blood = Blood(size=80)
    batch.add(blood)
    layer.add(batch)
    batch.position = director.get_window_size()[0]//2,director.get_window_size()[1]//2
    director.run(cocos.scene.Scene(layer))