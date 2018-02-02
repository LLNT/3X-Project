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
from display_item.sprite import Charactor, Cell
from display_item.state2color import *
from display_item.info import Personinfo
from display_item.menu import Ordermenu

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
        self.add(ColorLayer(0, 0, 0, 255, self.width, self.height))

        self.map = map  # type:map_controller.Main
        self.size = size
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
            self.people[pid] = Charactor(person, size, position[pid], controller[pid])
            self.add(self.people[pid])
            self.cells[position[pid]].person_on = pid
        self._clear_map()

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
        for person in self.people.values(): #type:Charactor
            person.color = per_state2color(person.state, person.controller)

        # according to the state of every sprite within, repaint them in the correct color
        pass

    def on_mouse_motion(self, x, y, buttons, modifiers):
        # use _repaint
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        # according to the state link to correct function
        if self.is_event_handler:
            print(self.state)
            self.mouse_pos = coordinate_t(x, y, self.size)
            self.mouse_btn = buttons
            self._state_control[self.state].__call__()
        pass

    def _reset(self):
        # reset to initial state
        pass

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
        if hasattr(self, 'info'):
            self.remove(self.info)
            del self.info
        self._mapstate = self.map.send_mapstate()
        for cell in self.cells.values():
            cell.state = 'default'
        for person in self.people.values(): #type:Charactor
            if person.state is not 'moved':
                person.state = 'unmoved'
        self._repaint()

    def _get_state_control(self):






        # 5   choose_attack
        # has selected a weapon. highlight the attack range
        # if valid target, turn to 6, else show the menu again
        # 6   confirm_attack
        # show battle_simulate info
        # if confirm, push battle scene and then return to 1, else turn to 5
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
            'confirm_attack': self._confirm_attack,6: self._confirm_attack
        }

    def _default(self):
        # 0   default
        # not any army is selected.
        # event handler should be true to wait for commands
        # consider end_turn only under this state
        if self.mouse_btn == 1:
            if self.cells[self.mouse_pos].person_on is not None: # just select a person
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
                self.menu = Ordermenu()
                self.add(self.menu)
                self.is_event_handler = False
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
        # show menu of move/attack/cancel
        # move: execute action and turn to 0
        # cancel: turn to 1
        # attack: show menu of weapon select
        pass

    def _choose_attack(self):
        pass

    def _confirm_attack(self):
        pass

    def attack(self):
        pass

    def move(self):
        valid = self._mapstate[0]
        action = self._sequential_move(self.selected, valid[self.selected][self.mouse_pos][1])
        obj = self.people[self.selected]
        obj.do(action + CallFunc(self._clear_map))
        pass

    def cancel(self):
        self.is_event_handler = True
        self._set_areastate([self.target], 'in_self_moverange')
        self.target = None
        pass

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
    pass