# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer, Layer
from cocos.scenes import FadeTransition
from cocos.scene import Scene
from display_item.text import Text
from battle import Battle
from display_item.ring import Scoreboard
from cocos.actions import Delay, CallFunc, MoveBy, MoveTo, FadeIn, FadeOut
from queue import Queue
from display_item.info import Experience

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
GRAY = (175, 175, 175)
class BattleSim(Layer):
    def __init__(self, maxsize=2):
        super().__init__()
        self.info = Queue(maxsize)
        self.width, self.height = director.get_window_size()[0], director.get_window_size()[1]
        self.flag = False

    def on_enter(self):
        super().on_enter()
        self.at, self.df, wp, self.map, pos = self.parent.battlelist
        self.battle = Battle(self.at, self.df, wp, self.df.item[0], self.map, pos)
        self.attacker = self.parent.people[self.at.pid]
        self.defender = self.parent.people[self.df.pid]
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']

        self.i = -1
        self.obj1 = self.attacker.right_ring
        self.obj2 = self.defender.right_ring
        self.get_battle_result()
        self.get_next_action()

    def get_battle_result(self):
        res = self.battle.battle()
        del self.battle
        self.events = res[0]
        self.content = res[1]

    def get_next_action(self, obj1=False, obj2=False):
        '''

        :return: the next action to call
        '''
        if self.obj1.busy or self.obj2.busy:
            return
        self.i += 1
        if self.i >= len(self.events):
            print(self.i)
            self.exit()
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
            obj_leave.do(MoveTo((self.width // 2, self.height), 1) | FadeOut(1))
        for obj in self.info.queue:
            obj.do(MoveBy((0, 40), 1))
        obj = Text(content=content, position=(self.width // 2, self.height // 2 + 50), color=color)
        self.add(obj)
        self.info.put(obj)
        obj.do(FadeIn(1.5) + CallFunc(self.get_next_action))

    def exit(self):
        if not self.flag:
            self.flag = True
            self.parent.remove(self)


    def growth(self):
        person = self.content[0]
        level = self.content[1]
        exp = self.content[2]
        growthlist = self.content[3]
        origin = self.content[4]
        self.exp = Experience(person=person, level=level, exp=exp, growthlist=growthlist, origin=origin)
        self.add(self.exp)



class Battlescene(BattleSim):
    is_event_handler = False
    def __init__(self, arena, w=640, h=480, maxsize=2):
        super(Battlescene, self).__init__(maxsize)

        self.at, self.df, wp, self.map, pos = arena.battlelist
        self.battle = Battle(self.at, self.df, wp, self.df.item[0], self.map, pos)
        pos1 = w // 4, h // 3
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']
        self.arena = arena
        self.attacker = Scoreboard(pos1, 0.4, prop=self.hp1 / self.mhp1,
                                   back_color = BLACK, hp=self.hp1, mhp=self.mhp1)
        pos2 = w  * 3 // 4, h // 3
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']
        self.defender = Scoreboard(pos2, 0.4, prop=self.hp2 / self.mhp2,
                                   back_color = BLACK, hp=self.hp2, mhp=self.mhp2)

        self.add(self.attacker)
        self.add(self.defender)


        self.w = w
        self.h = h
        self.i = -1
        self.obj1 = self.attacker.right_ring
        self.obj2 = self.defender.right_ring
        self.info = Queue(maxsize)
        self.get_battle_result()
        self.get_next_action()
        '''info = Info()
        self.add(info)
        content = []
        for event in res:
            content.append(str(event[0])+','+event[1])
        info.display(content)'''

    def on_enter(self):
        Layer.on_enter(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.remove(self.exp)
        self.do(CallFunc(self._return_arena)+ Delay(0.5) + CallFunc(self._pop))

    def _return_arena(self):
        director.window.remove_handlers(self)
        director.push(FadeTransition(Scene(ColorLayer(0, 0, 0, 0, self.w, self.h)), duration=1.5))

    def _pop(self):
        self.arena.on_return()
        director.pop()
        director.pop()
        del self

    def exit(self):
        if not self.flag:
            for info in self.info.queue:
                self.remove(info)
            self.growth()
            self.flag = True

