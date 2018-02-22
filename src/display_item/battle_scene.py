# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 18:36
'''

from cocos.director import director
from cocos.layer import ColorLayer, Layer
from cocos.scenes import FadeTransition
from cocos.scene import Scene
from cocos.sprite import Sprite
from display_item.text import Text
from battle import Battle
from display_item.ring import Scoreboard
from cocos.actions import Delay, CallFunc, MoveBy, MoveTo, FadeIn, FadeOut
from queue import Queue
from display_item.info import Experience
from wand import *
from display_item.dialog import Battledialog
from display_item.eventdisplay import Eventdisplay

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
GRAY = (175, 175, 175)
class Animation(Layer):
    '''
    the base class for animations displaying
    recieves battle result and the playing object, plays them in the correct order

    '''
    def __init__(self, obj1, obj2, at, df, arena, maxsize=2, width=640, height=480):
        super().__init__()
        self.info = Queue(maxsize)
        self.flag = False
        self.attacker = obj1
        self.defender = obj2
        self.at = at
        self.df = df
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']
        self.obj1 = self.attacker.right_ring
        self.obj2 = self.defender.right_ring
        self.i = -1
        self.width = width
        self.height = height
        self.map = arena.map #type:map_controller.Main
        self.item = None
        self.getitem = None
        self.transtuple = None
        pid2dir = {}
        pid2dir[self.at.pid] = 'left'
        pid2dir[self.df.pid] = 'right'
        self.dialog_info = {'pid2dir':pid2dir}
        self.defeat = None

    def excute(self, event):
        self.events = event[0]
        self.content = event[1]
        battlebefore = event[2]
        self.dialogafter = event[3]
        if len(battlebefore) > 0:
            _event = battlebefore[-1]
            # should be replaced by condition
            self.add(Eventdisplay(
                event=_event, map=self.map, dialog_type='B', dialog_info=self.dialog_info,
                w=self.width, h=self.height, callback=self.get_next_action
            ))

        else:
            self.get_next_action()


    def get_next_action(self):
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
                    self.defeat = self.at.pid
                elif event[0] is -2:
                    self.map.defeated_character(self.at.pid)
                    self.defeat = self.df.pid

            elif content is 'Getitem':
                self.getitem = self.item
            self.add_new_infos(content)
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
        obj = Text(text=content, position=(self.width // 2, self.height // 2 + 50),
                   color=color, font_size=30)
        self.add(obj)
        self.info.put(obj)
        obj.do(FadeIn(1.5) + CallFunc(self.get_next_action))

    def exit(self):
        '''
        should be override to define the movement when exit
        :return:
        '''
        if self.dialogafter is not None:
            self.dialog_info['E'] = self.defeat
            self.add(Eventdisplay(
                event=self.dialogafter, map=self.map, dialog_type='B',w=self.width, h=self.height,
                dialog_info=self.dialog_info, callback=self.growth
            ))
            self.map.global_vars.flags[self.dialogafter['Event']] = True
        else:
            self.growth()

        pass

    def growth(self):
        person = self.content[0]
        level = self.content[1]
        exp = self.content[2]
        growthlist = self.content[3]
        origin = self.content[4]
        self.exp = Experience(person=person, level=level, exp=exp, growthlist=growthlist, origin=origin)
        self.add(self.exp)

class Battlescene(Animation):
    is_event_handler = False
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, self.df, wp, self.map, pos = arena.battlelist
        self.at.equip(wp)
        wp_d = self.df.get_equip()
        self.battle = Battle(self.at, self.df, wp, wp_d, self.map, pos)
        pos1 = w // 4, h // 3
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']
        self.attacker = Scoreboard(pos1, 0.4, prop=self.hp1 / self.mhp1,
                                   back_color = BLACK, hp=self.hp1, mhp=self.mhp1)
        pos2 = w  * 3 // 4, h // 3
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']
        self.defender = Scoreboard(pos2, 0.4, prop=self.hp2 / self.mhp2,
                                   back_color = BLACK, hp=self.hp2, mhp=self.mhp2)

        self.arena = arena
        super(Battlescene, self).__init__(
            obj1=self.attacker,
            obj2=self.defender,
            at=self.at,
            df=self.df,
            arena=arena,
            width=w,
            height=h,
            maxsize=maxsize
        )
        self.add(self.attacker)
        self.add(self.defender)
        # self.add_battle_card(w, h)
        event = self.battle.battle()
        del self.battle
        self.excute(event=event)

    def on_mouse_press(self, x, y, buttons, modifiers):

        self.arena.on_return(self.at, self.getitem, self.transtuple)
        self.kill()
        director.window.remove_handlers(self)
        director.pop()

    def exit(self):
        if not self.flag:
            for info in self.info.queue:
                self.remove(info)
            self.flag = True
            super().exit()

    def add_battle_card(self, w, h):
        btca, btcd = self.battle.get_battlecard()
        self.add(Sprite(btca, position=(w//4, h*3//4)))
        self.add(Sprite(btcd, position=(w*3//4, h*3//4)))
        
class Wandscene(Battlescene):
    def excute(self, event):
        self.events = event[0]
        self.content = event[1]
        self.get_next_action()
        
    def exit(self):
        if not self.flag:
            for info in self.info.queue:
                self.remove(info)
            self.flag = True
            self.growth()

    def wandinit(self, wand, w, h, arena, maxsize):

        pos1 = w // 4, h // 4
        self.hp1, self.mhp1 = self.at.ability['HP'], self.at.ability['MHP']
        self.attacker = Scoreboard(pos1, 0.4, prop=self.hp1 / self.mhp1,
                                   back_color=BLACK, hp=self.hp1, mhp=self.mhp1)
        pos2 = w * 3 // 4, h // 4
        self.hp2, self.mhp2 = self.df.ability['HP'], self.df.ability['MHP']
        self.defender = Scoreboard(pos2, 0.4, prop=self.hp2 / self.mhp2,
                                   back_color=BLACK, hp=self.hp2, mhp=self.mhp2)

        self.arena = arena
        super(Battlescene, self).__init__(
            obj1=self.attacker,
            obj2=self.defender,
            at=self.at,
            df=self.df,
            arena=arena,
            width=w,
            height=h,
            maxsize=maxsize
        )
        self.add(self.attacker)
        self.add(self.defender)
        # self.add_battle_card(w, h)


class Wandtype0(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map = arena.wandlist_type0
        self.battle = Type0(self.at, wand, self.df, self.map)
        self.wandinit(wand, w, h, arena, maxsize)
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

    def get_next_action(self):
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
                    self.defeat = self.at.pid
                elif event[0] is -2:
                    self.map.defeated_character(self.at.pid)
                    self.defeat = self.df.pid
            self.add_new_infos(content)
            pass
        else:
            hit, dmg, amg = event[1].split(',')
            dmg = int(dmg)
            amg = int(amg)
            if event[0] is 1:
                self.hp2 += dmg
                self.hp1 -= amg
                if hit is 'H':
                    content = "Heal by " + str(dmg) + ' Damage'
                elif hit is 'C':
                    content = 'Critical Attack by ' + str(dmg) + ' Damage'
                elif hit is 'M':
                    content = 'Miss'
                    color = (255, 0, 0, 255)
                else:
                    content = 'oooops'
            elif event[0] is 2:
                color = (255, 255, 0, 255)
                self.hp1 += dmg
                self.hp2 -= amg
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

class Wandtype1(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos = arena.wandlist_type1
        self.battle = Type1(self.at, wand, self.df, self.map)
        self.wandinit(wand, w, h, arena, maxsize)
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

class Wandtype2(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, item = arena.wandlist_type2
        self.battle = Type2(self.at, wand, self.df, self.map, item)
        self.wandinit(wand, w, h, arena, maxsize)
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)


class Wandtype3(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos, item = arena.wandlist_type3
        self.battle = Type3(self.at, wand, self.df, self.map, pos, item)
        self.wandinit(wand, w, h, arena, maxsize)
        self.item = item
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

class Wandtype4(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        user, wand, target, self.map= arena.wandlist_type4
        self.battle = Type4(user, wand, self.map, target)
        super(Layer, self).__init__()
        self.width = w
        self.height = h
        self.arena = arena
        self.at = user
        self.getitem = None
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)
        self.transtuple = user.pid, target


    def excute(self, event):
        self.events = event[0]
        self.content = event[1]
        self.growth()

class Wandtype5(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos, tarpos = arena.wandlist_type5
        self.battle = Type5(self.at, wand, self.df, self.map, pos, tarpos)
        self.wandinit(wand, w, h, arena, maxsize)
        self.transtuple = self.df.pid, tarpos
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

class Wandtype6(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos = arena.wandlist_type6
        self.battle = Type6(self.at,wand, self.df,self.map, pos)
        self.transtuple_c = self.df.pid, self.battle.get_target()
        self.wandinit(wand, w, h, arena, maxsize)
        self.transtuple = self.transtuple_c
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

class Wandtype7(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos = arena.wandlist_type7
        self.battle = Type7(self.at,wand, self.df,self.map, pos)
        self.wandinit(wand, w, h, arena, maxsize)
        self.transtuple = self.df.pid, pos
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)

class Wandtype8(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        user, wand, self.map, pos= arena.wandlist_type8
        self.battle = Type8(user, wand, self.map, pos)
        super(Layer, self).__init__()
        self.width = w
        self.height = h
        self.arena = arena
        self.at = user
        self.getitem = None
        event = self.battle.execute()
        del self.battle
        self.excute(event=event)
        self.transtuple = None


    def excute(self, event):
        self.events = event[0]
        self.content = event[1]
        self.growth()

class Wandtype9(Wandscene):
    def __init__(self, arena, w=640, h=480, maxsize=2):
        self.at, wand, self.df, self.map, pos = arena.wandlist_type9
        self.battle = Type9(self.at,wand, self.df,self.map, pos)
        self.wandinit(wand, w, h, arena, maxsize)