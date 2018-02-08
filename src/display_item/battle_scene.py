# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer
from cocos.scenes import FadeTransition
from cocos.scene import Scene
from display_item.text import Text
from battle import Battle
from cocos.sprite import Sprite
from cocos.layer import Layer
from cocos.actions import RotateTo, RotateBy, Delay, CallFunc, MoveBy, MoveTo, FadeIn, FadeOut
from queue import Queue

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

class Battlescene(ColorLayer):
    is_event_handler = False
    def __init__(self, battlelist, w=800, h=600, maxsize=2):
        super(Battlescene, self).__init__(255,255,255,255,width=w, height=h)

        self.at, self.df, wp, self.map, pos = battlelist
        battle = Battle(self.at, self.df, wp, self.df.item[0], self.map, pos)
        pos1 = w // 4, h // 3
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']

        self.attacker = Ring(pos1, 0.4, prop=self.hp1 / self.mhp1, back_color = WHITE, hp=self.hp1, mhp=self.mhp1)
        pos2 = w  *6 // 11, h // 3
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']
        self.defender = Ring(pos2, 0.4, prop=self.hp2 / self.mhp2,back_color = WHITE, hp=self.hp2, mhp=self.mhp2)

        self.add(self.attacker)
        self.add(self.defender)

        res = battle.battle()
        del battle
        self.w = w
        self.h = h
        action1 = action2 = Delay(0.5)

        self.events = res
        self.i = -1
        self.obj1 = self.attacker.right_ring
        self.obj2 = self.defender.right_ring


        '''for event in res:
            print(event)
            if event[0] < 0:
                continue
            hit,dmg,amg = event[1].split(',')
            dmg = int(dmg)
            amg = int(amg)
            if hit is 'H':
                if event[0] is 1:
                    self.hp2 -= dmg
                    self.hp1 += amg
                elif event[0] is 2:
                    self.hp1 -= dmg
                    self.hp2 += amg
                # p1.set_angle(hp1 / mhp1)
                # p2.set_angle(hp2 / mhp2)
                _, a1 = self.attacker.set_angle_action(self.hp1 / self.mhp1)
                _, a2 = self.defender.set_angle_action(self.hp2 / self.mhp2)
                action1 = action1 + a1
                action2 = action2 + a2
            else:
                continue
        
        self.obj1.do(action1)
        self.obj2.do(action2)'''
        self.info = Queue(maxsize)
        self.get_next_action()
        '''info = Info()
        self.add(info)
        content = []
        for event in res:
            content.append(str(event[0])+','+event[1])
        info.display(content)'''

    def get_next_action(self, obj1=False, obj2=False):
        '''

        :return: the next action to call
        '''

        if self.obj1.busy or self.obj2.busy:
            return
        self.i += 1
        if self.i >= len(self.events):
            if self.i == len(self.events):
                director.window.push_handlers(self)
            return
        event = self.events[self.i]
        print(event)
        color = (0, 255, 0, 255)
        if event[0] < 0: # show info on screen
            content = event[1]
            if content is 'Defeatenemy':
                if event[0] is -1:
                    self.map.defeated_character(self.df.pid)
                elif event[0] is -2:
                    self.map.defeated_character(self.at.pid)
            self.add_new_infos(content)
            pass
        else:
            hit, dmg, amg = event[1].split(',')
            dmg = int(dmg)
            amg = int(amg)
            if event[0] is 1:
                self.hp2 -= dmg
                self.hp1 += amg
                if hit is 'H':
                    content = "Hit by " + str(dmg) + ' Damage'
                elif hit is 'C':
                    content = 'Critical Attack by ' + str(dmg) + ' Damage'
                elif hit is 'M':
                    content = 'Miss'
                    color = (255, 0, 0, 255)
                else:
                    content = 'oooops'
            elif event[0] is 2:
                color = (255, 255, 0, 255)
                self.hp1 -= dmg
                self.hp2 += amg
                if hit is 'H':
                    content = "Counter by " + str(dmg) + ' Damage'
                elif hit is 'C':
                    content = 'Critical Reflect by ' + str(dmg) + ' Damage'
                elif hit is 'M':
                    content = 'Counter Miss'
                    color = (255, 0, 0, 255)
                else:
                    content = 'oooops'
            self.add_new_infos(content, color)

            t1, a1 = self.attacker.set_angle_action(self.hp1 / self.mhp1)
            t2, a2 = self.defender.set_angle_action(self.hp2 / self.mhp2)
            t1.busy = t2.busy = True
            t1.do(a1 + CallFunc(t1.parent.set_busy) + CallFunc(self.get_next_action))
            t2.do(a2 + CallFunc(t2.parent.set_busy) + CallFunc(self.get_next_action))



            # show leaving effect
            pass

    def add_new_infos(self, content, color = (0, 255, 0, 255)):
        if self.info.full():
            obj_leave = self.info.get()
            obj_leave.do(MoveTo((self.width // 3, self.height), 1))
        for obj in self.info.queue:
            obj.do(MoveBy((0, 40), 1))
        obj = Text(content=content, position=(self.width // 3, self.height // 2), color=color)
        self.add(obj)
        self.info.put(obj)
        obj.do(FadeIn(1.5) + CallFunc(self.get_next_action))

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.do(CallFunc(self._return_arena)+ Delay(1) + CallFunc(self._pop))


    def _return_arena(self):
        director.window.remove_handlers(self)
        director.push(FadeTransition(Scene(ColorLayer(0, 0, 0, 0, self.w, self.h)), duration=1.5))

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
        self.right_ring.busy = False
        angle = 360 - prop * 360
        self.angles = angle
        if angle > 180:
            self.mask_visible()
        else:
            self.left_visible()
        self.right_ring.rotation = angle
        self.schedule(self.update)

    def set_busy(self):
        self.right_ring.busy = False

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

    def set_angle_action(self, proportion, duration=4):
        angle = 360 - proportion * 360
        delta = abs(self.angles - angle)
        if delta <= 10:
            return self.right_ring, Delay(0.5)
        duration = min(1, delta/90) * duration
        if self.angles > angle: # right rotation
            if angle >= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(180, duration) + CallFunc(self.change_angle, angle))
            elif self.angles <= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = duration * (self.angles - 180) / delta
                d2 = duration - d1
                return self.right_ring, (Delay(0.5) + RotateTo(180, d1)
                                   + RotateTo(angle, d2) + CallFunc(self.change_angle, angle))
        else: #
            if angle <= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            elif self.angles >= 180:
                return self.right_ring, (Delay(0.5) + RotateTo(angle, duration) + CallFunc(self.change_angle, angle))
            else:
                d1 = duration * (180 - self.angles) / delta
                d2 = duration - d1
                return self.right_ring, (Delay(0.5) + RotateBy(180 - self.angles, d1)
                                   + RotateTo(angle, d2) + CallFunc(self.change_angle, angle))

    def update(self, dt):

        r = (self.right_ring.rotation) / 360
        if r == 0 and self.angles == 360:
            r = 1
        if r > 0.5:
            self.mask_visible()
        else :
            self.left_visible()


        color = [0, 0, 0]
        for i in range(3):
            color[i] = int(r * self.delta[i] + self.start_color[i])
        self.right_ring.color = color
        self.left_ring.color = color
        self.hp.element.text = str(self.mhp - int(r * self.mhp))
        self.hp.element.color = color[0], color[1],color[2], 255

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

