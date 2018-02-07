# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:02
'''
import pyglet

from cocos.layer import Layer, ColorLayer
from cocos.director import director
from cocos.scene import Scene
from cocos.actions import CallFunc, MoveTo, Delay
from cocos.scenes import FadeTransition
from display_item.sprite import Charactor, Cell, Endturn
from display_item.state2color import *
from display_item.info import Personinfo, Battleinfo
from display_item.menu import Ordermenu, Weaponmenu
from display_item.background import Background
from display_item.battle_scene import Battlescene

import map_controller
from global_vars import Main as Global
from data_loader import Main as Data
from person_container import Main as Person_Container
from terrain_container import Main as Terrain_Container



class Arena(Layer):
    # the holder of map and roles
    is_event_handler = True

    def __init__(self, map, w, h, size=80):
        super(Arena, self).__init__()

        # initialize the holder according to the map
        self.width, self.height = w*size, h*size

        self.add(Background(self.width, self.height))
        # self.add(ColorLayer(100, 100, 100, 255, self.width, self.height))

        self.map = map  # type:map_controller.Main
        self.size = size
        self.w, self.h = w, h
        # initialize arena attributes
        self._state_control = self._get_state_control()


        # add map elements
        self.cells = {}
        self.people = {}
        for i in range(w):
            for j in range(h):
                self.cells[(i, j)] = Cell(size, (i, j))
                self.add(self.cells[(i, j)])

        people = map.person_container.people
        position = map.person_container.position
        controller = map.person_container.controller
        for person in people:
            pid = person.pid
            self.people[pid] = Charactor(person, 0.9, size, position[pid], controller[pid])
            self.add(self.people[pid])
            self.cells[position[pid]].person_on = pid
        self._clear_map()
        button = Endturn(label='END',scale=0.4,pos=(560,200),color=MAROON, font_size=48)
        self.add(button)



        self.next_round()


    def next_round(self):
        self.map.turn += 1
        self.set_turn(self.map.turn)
        self.map.controller = 0
        self._mapstate = self.map.send_mapstate()
        for p in self.people.values():
            p.state = 'unmoved'
        self._repaint()
        if self.map.turn > 6:
            director.pop()
        else:
            self.map.take_turn(self)

    def _sequential_move(self, pid, dst):
        # move person of pid through the trace dst
        map = self.map
        self.cells[map.person_container.position[pid]].person_on = None
        map.person_container.position[pid] = dst[-1]
        map.person_container.movable[pid] = False
        self._mapstate = self.map.send_mapstate()
        self.people[pid].state = 'moved'
        self.is_event_handler = False
        self.cells[dst[-1]].person_on = pid
        action = Delay(0.1)
        for x,y in dst:
            action = action + MoveTo(coordinate(x, y, self.size), 0.5)
        return action

    def _repaint(self):
        for cell in self.cells.values():
            cell.color = mapstate2color[cell.state]
            cell.opacity = opacity[cell.state]
        for person in self.people.values(): #type:Charactor
            person.color = per_state2color(person.state, person.controller)

        # according to the state of every sprite within, repaint them in the correct color
        pass

    def on_mouse_motion(self, x, y, buttons, modifiers):
        # use _repaint
        if self.is_event_handler:
            i, j = coordinate_t(x, y, self.size)
            if i < self.w and j < self.h:
                self._repaint()
                cell = self.cells[(i, j)]
                cell.color = mapstate2color_motion[cell.state]
                cell.opacity = opacity[cell.state]
            pass

    def _in_arena(self):
        i, j = self.mouse_pos
        if i < self.w and j < self.h:
            return True
        else:
            return False

    def on_mouse_press(self, x, y, buttons, modifiers):
        # according to the state link to correct function
        if self.is_event_handler:
            print(self.state)
            self.mouse_pos = coordinate_t(x, y, self.size)
            self.mouse_btn = buttons
            self._state_control[self.state].__call__()
        pass

    def _reset(self):
        # reset to last state
        # specificlly handle with choose_attack
        if self.state is 'choose_attack':
            self.remove(self.wpinfo)
            self.attack()
            pid = self.selected
            valid = self._mapstate[0]
            for (i, j) in self.cells.keys():
                cell = self.cells[(i, j)]
                if cell.state is 'in_self_attackrange':
                    if (i, j) in valid[pid]:
                        cell.state = 'in_self_moverange'
                    else:
                        cell.state = 'default'
            self.state = 'valid_dst'
            self.item = None
        elif self.state is 'choose_support':
            for pid in self.sup_dict:
                self.people[pid].state = self._reset_person[pid]
            self.state = 'valid_dst'
            self.menu = Ordermenu(self)
            self._add_menu(self.menu)
            self.is_event_handler = False
        self._repaint()
        pass

    def _seq_add(self, item):
        self.add(item)


    def _add_menu(self, menu, dt=0.5):
        self.do(Delay(dt) + CallFunc(self._seq_add, menu))

    def _set_areastate(self, area, state):
        for i, j in area:
            self.cells[(i, j)].state = state
        self._repaint()

    def _clear_map(self):
        self.is_event_handler = True
        self.state = 'default'
        self.selected = None
        self.target = None
        self.mouse_pos = None
        self.mouse_btn = 0
        self.item = None
        self.sup_dict = None
        self._reset_person = {}
        try:
            self.remove(self.info)
            self.remove(self.wpinfo)
        except:
            pass

        self._mapstate = self.map.send_mapstate()
        for cell in self.cells.values():
            cell.state = 'default'
        for person in self.people.values(): #type:Charactor
            if person.state is not 'moved':
                person.state = 'unmoved'
        self._repaint()

    def _get_state_control(self):
        '''
        :return: dictionary in self._state_control
        :usage: self._state_control[state].__call__()
        '''
        return {
            'default':self._default, 0:self._default,
            'valid_select': self._valid_select,1: self._valid_select,
            'invalid_select': self._invalid_select,2: self._invalid_select,
            'person_info': self._person_info,3: self._person_info,
            'valid_dst': self._valid_dst,4: self._valid_dst,
            'choose_attack': self._choose_attack,5: self._choose_attack,
            'confirm_attack': self._confirm_attack,6: self._confirm_attack,
            'show_battle_result': self._show_battle_result, 7 : self._show_battle_result,
            'choose_support': self._choose_support, 8: self._choose_support
        }

    def _default(self):
        # 0   default
        # not any army is selected.
        # event handler should be true to wait for commands
        # consider end_turn only under this state
        if self.mouse_btn == 1:
            if not self._in_arena():
                pass
            elif self.cells[self.mouse_pos].person_on is not None: # just select a person
                pid = self.cells[self.mouse_pos].person_on
                self.people[pid].state = 'selected'
                self.selected = pid
                valid, invalid, ally, enemy = self._mapstate
                if pid in valid.keys():   # a valid person selected
                    area = valid[pid]
                    self.state = 'valid_select'
                else:
                    self.state = 'invalid_select'
                    if pid in invalid.keys():
                        area = set()
                        self.people[pid].state = 'moved'
                    elif pid in ally.keys():
                        area = ally[pid]
                    elif pid in enemy.keys():
                        area = enemy[pid]
                    else:
                        area = set()
                        pass
                self._set_areastate(area, ctrl2map_moverange[self.map.person_container.controller[pid]])
            else:
                self._clear_map()
                pass
        else:
            if self.cells[self.mouse_pos].person_on is not None:
                pid = self.cells[self.mouse_pos].person_on
                select = self.people[pid].person
                self.info = Personinfo(select)
                self.add(self.info)
                self.state = 'person_info'
            pass

    def _valid_select(self):
        # 1   valid_select
        # a self army is selected. highlight the move range and wait for another command
        # if a valid target is selected turn to 4, else show info and retain this state
        if self.mouse_btn == 1:
            valid = self._mapstate[0]
            if self.mouse_pos in valid[self.selected]:
                self.target = self.mouse_pos
                self._set_areastate([self.target], 'target')
                self.menu = Ordermenu(self)
                self._add_menu(self.menu)
                self.is_event_handler = False
                self.state = 'valid_dst'
            else:
                pass
        elif self.mouse_btn == 4:
            self._clear_map()
        pass

    def _invalid_select(self):
        # 2   invalid_select
        # an ally or enemy is selected. just highlight the move range. maybe display the info.
        # any command should return to default
        self._clear_map()
        pass

    def _person_info(self):
        # 3   person_info
        # displaying person info.
        # any command should return
        self._clear_map()
        pass

    def _valid_dst(self):
        # 4   valid_dst
        # is showing menu of move/attack/cancel
        # move: execute action and turn to 0
        # cancel: turn to 1
        # attack: show menu of weapon select

        # at present has nothing to do
        pass

    def _choose_attack(self):
        # 5   choose_attack
        # has selected a weapon. highlight the attack range
        # if valid target, turn to 6, else show the menu again, clear the attack_range and reshow the move_range
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena():
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_attackrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is 1:
                self.wpinfo.visible = False
                at = self.people[self.selected].person
                df = self.people[cell.person_on].person
                wp = self.item
                self.info = Battleinfo(at, df, wp, self.map, self.target)
                self.battlelist = [at, df, wp, self.map, self.target]
                self.add(self.info)
                self.state = 'confirm_attack'
            else:
                self._reset()
            pass
        pass

    def _confirm_attack(self):
        # 6   confirm_attack
        # showing battle_simulate info
        # if confirm, push battle scene and then return to 1, else turn to 5
        self.remove(self.info)
        if self.mouse_btn is 4:
            self.state = 'choose_attack'
            self.wpinfo.visible = True
        elif self.mouse_btn is 1:
            valid = self._mapstate[0]
            action = self._sequential_move(self.selected, valid[self.selected][self.target][1])
            obj = self.people[self.selected]
            obj.do(action + CallFunc(self._push_battle_scene, self.battlelist) + CallFunc(self._clear_map))
            self.state = 'show_battle_result'
            pass

        pass

    def _push_battle_scene(self, res):
        director.push(FadeTransition(Scene(Battlescene(res)), duration=1.5))

    def _show_battle_result(self):
        # 7   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5
        pass

    def _choose_support(self):
        if self.mouse_btn is 1:
            if self.mouse_pos in self.sup_dict.values():
                self.map.build_support(self.selected, self.cells[self.mouse_pos].person_on)
                for pid in self.sup_dict:
                    self.people[pid].state = self._reset_person[pid]
                self.move()
        elif self.mouse_btn is 4:
            self._reset()
        pass

    def select_target(self, item):
        area = []
        max_range = item.itemtype.max_range
        min_range = item.itemtype.min_range
        (i, j) = self.target
        for distance in range(min_range, max_range + 1):
            for dx in range(distance + 1):
                dy = distance - dx
                for x, y in [(i + dx, j + dy), (i + dx, j - dy), (i - dx, j + dy), (i - dx, j - dy)]:
                    if x in range(self.w) and y in range(self.h):
                        area.append((x, y))
        self._set_areastate(area, 'in_self_attackrange')
        self.state = 'choose_attack'
        self.item = item
        self.is_event_handler = True

    def support(self, sup_dict):
        self.is_event_handler = True
        self.state = 'choose_support'
        for pid in sup_dict:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_support'
        self.sup_dict = sup_dict
        self._repaint()

    def attack(self):
        self.is_event_handler = False
        self._set_areastate([self.target], 'target')
        items = self.people[self.selected].person.item

        self._add_menu(Weaponmenu(items, self.map))
        pass

    def end_turn(self):
        self._clear_map()
        self.map.controller = 1
        self.map.reset_state(0)
        self.is_event_handler = False
        self.map.ai_turn2(self)

    def move(self):
        valid = self._mapstate[0]
        action = self._sequential_move(self.selected, valid[self.selected][self.target][1])
        obj = self.people[self.selected]
        obj.do(action + CallFunc(self._clear_map))
        pass

    def enemy_move(self, pid, dst, rng):
        self._set_areastate(rng, 'in_enemy_moverange')
        action = self._sequential_move(pid, dst)
        obj = self.people[pid]

        obj.do(action + CallFunc(self._clear_map) + CallFunc(self.map.take_turn, self))
        pass

    def cancel(self):
        self.is_event_handler = True
        self._set_areastate([self.target], 'in_self_moverange')
        self.state = 'valid_select'
        self.target = None
        pass

    def set_turn(self, turn):
        # change the turn over the arena
        pass

    def remove(self, obj):
        super().remove(obj)
        del obj

def map_init():
    data = Data()
    global_vars = Global(data)
    terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
    person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
    map = map_controller.Main(terrain_container_test, person_container_test, global_vars)
    w = terrain_container_test.M
    h = terrain_container_test.N
    return map, w, h

def coordinate_t(x, y, size):
    i = x // size
    j = y // size
    return i, j

def coordinate(i, j, size):
    x = i * size + size // 2
    y = j * size + size // 2
    return x, y



if __name__ == '__main__':
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init(caption='3X-Project')
    map, w, h = map_init()
    director.run(Scene(Arena(map, w, h)))
    map_init()




