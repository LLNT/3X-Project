# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer
from cocos.scenes import ShuffleTransition
from cocos.scene import Scene
from display_item.text import Text
from battle import Battle
from cocos.sprite import Sprite
from cocos.layer import Layer
from cocos.actions import RotateTo, RotateBy, Delay, CallFunc
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

class Battlescene(ColorLayer):
    is_event_handler = True
    def __init__(self, battlelist, w=800, h=600):
        super(Battlescene, self).__init__(255,255,255,255,width=w, height=h)
        at, df, wp, map, pos = battlelist
        battle = Battle(at, df, wp, df.item[0], map, pos)
        pos1 = w // 4, h // 3
        hp1, mhp1 = at.ability['HP'], at.ability['MHP']
        p1 = Ring(pos1, 0.4, prop=hp1 / mhp1, back_color = WHITE, hp=hp1, mhp=mhp1)
        pos2 = w  *6 // 11, h // 3
        hp2, mhp2 = df.ability['HP'], df.ability['MHP']
        p2 = Ring(pos2, 0.4, prop=hp2 / mhp2,back_color = WHITE, hp=hp2, mhp=mhp2)
        self.add(p1)
        self.add(p2)

        res = battle.battle()
        del battle
        self.w = w
        self.h = h
        print(res)
        action = Delay(0.5)
        for event in res:
            if event[0] < 0:
                continue
            hit,dmg,amg = event[1].split(',')
            dmg = int(dmg)
            amg = int(amg)
            print(hp1, hp2)
            if hit is 'H':
                if event[0] is 1:
                    hp2 -= dmg
                    hp1 += amg
                elif event[0] is 2:
                    hp1 -= dmg
                    hp2 += amg
                print(hp1, hp2)
                p1.set_angle(hp1 / mhp1)
                p2.set_angle(hp2 / mhp2)
            else:
                continue

        '''info = Info()
        self.add(info)
        content = []
        for event in res:
            content.append(str(event[0])+','+event[1])
        info.display(content)'''



    def on_mouse_press(self, x, y, buttons, modifiers):
        self.do(CallFunc(self._return_arena)+ Delay(1) + CallFunc(self._pop))

    def _return_arena(self):
        director.push(ShuffleTransition(Scene(ColorLayer(0, 0, 0, 0, self.w, self.h)), duration=1.5))

    def _pop(self):
        director.pop()
        director.pop()
        del self

class Ring(Layer):

    def __init__(self, postion, scale, start_color=GREEN, end_color=RED, prop=1,back_color = BLACK, hp=20, mhp=20):
        super().__init__()
        self.start_color = start_color
        self.end_color = end_color

        self.delta = self._diff(self.end_color, self.start_color)

        self.left_ring = Sprite(image='ring_right.png', color=start_color, position=postion,
                                             scale=scale, rotation=180)

        self.right_ring = Sprite(image='ring_right.png', position=postion, scale=scale,
                                              color=start_color)

        self.mask_ring = Sprite(image='ring_right.png', position=postion, scale=scale,
                                             color=back_color)

        self.hp = Text(str(hp), postion,color=(0,0,0,255))
        self.add(self.hp)
        self.mhp = mhp
        self.add(self.left_ring)
        self.add(self.right_ring)
        self.add(self.mask_ring)
        angle = 360 - prop * 360
        print(angle)
        self.angles = angle
        if angle > 180:
            self.mask_visible()
        else:
            self.left_visible()
        self.right_ring.rotation = angle
        self.schedule(self.update)

    def set_angle(self, proportion, duration=4):
        angle = 360 - proportion * 360
        delta = abs(self.angles - angle)
        if delta <= 10:
            return
        duration = min(1, delta/90) * duration
        if self.angles > angle: # right rotation
            if angle >= 180:
                self.right_ring.do(Delay(0.5) + RotateTo(180, duration) + CallFunc(self.change_angle, angle))
            elif self.angles <= 180:
                self.left_visible()
                self.right_ring.do(Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = duration * (self.angles - 180) / delta
                d2 = duration - d1
                self.right_ring.do(Delay(0.5) + RotateTo(180, d1) + CallFunc(self.left_visible)
                                   + RotateTo(angle, d2) + CallFunc(self.change_angle, angle))
        else: #
            if angle <= 180:
                self.left_visible()
                self.right_ring.do(Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            elif self.angles >= 180:
                self.mask_visible()
                self.right_ring.do(Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = duration * (180 - self.angles) / delta
                d2 = duration - d1
                self.right_ring.do(Delay(0.5) + RotateBy(180 - self.angles, d1) + CallFunc(self.mask_visible)
                                   + RotateTo(angle, d2) + CallFunc(self.change_angle, angle))

    def update(self, dt):
        r = (self.right_ring.rotation) / 360
        color = [0, 0, 0]
        for i in range(3):
            color[i] = r * self.delta[i] + self.start_color[i]
        self.right_ring.color = color
        self.left_ring.color = color
        self.hp.element.text = str(self.mhp - int(r * self.mhp))

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

