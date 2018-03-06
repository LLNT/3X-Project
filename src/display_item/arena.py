# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:02
'''
import pyglet
import json
from cocos.layer import Layer, ColorLayer, ScrollableLayer
from cocos.director import director
from cocos.scene import Scene
from cocos.actions import CallFunc, MoveTo, Delay, FadeTo, FadeIn, FadeOut, Place
from cocos.scenes import FadeTransition
from display_item.sprite import Charactor, Cell
from display_item.state2color import *
from display_item.info import Personinfo, Battleinfo, Experience2
from display_item.menu import *
from display_item.background import Background
from display_item.battle_scene import *
from display_item.ring import PerSpr
from display_item.getitem import Getitem
from display_item.action_control import Sequencial, Graphic
from display_item.dialog import Dialogscene
from display_item.eventdisplay import *
import os
import map_controller
from global_vars import Main as Global
from data_loader import Main as Data
from person_container import Main as Person_Container
from terrain_container import Main as Terrain_Container
from wand import Type1, Type3, Type5
from typing import Dict

class Arena(ScrollableLayer):
    # the holder of map and roles
    is_event_handler = False

    def __init__(self, map, menulayer,infolayer,size=80):
        super(Arena, self).__init__()

        # initialize the holder according to the map
        self.map = map  # type:map_controller.Main
        self.size = size
        self.w, self.h = map.terrain_container.M, map.terrain_container.N
        self.width, self.height = self.w*size, self.h*size
        self.windowsize = director.get_window_size()
        self.anchor = self.width // 2, self.height // 2

        self.add(Background(self.windowsize, self.map.pic))

        # initialize arena attributes
        self._state_control = self._get_state_control() #type: Dict[str, callable]
        self.general = self.map.eventlist['General']
        self.general_length = len(self.general)
        self.turn_event = self.map.eventlist['Turns']
        self.turn_length = len(self.turn_event)

        # add map elements
        self.cells = {}  #type:Dict[tuple,Cell]
        self.people = {} #type:Dict[str,PerSpr]
        self.person_layer = Layer()
        self.add(self.person_layer)
        for i in range(self.w):
            for j in range(self.h):
                self.cells[(i, j)] = Cell(size, (i, j))
                self.person_layer.add(self.cells[(i, j)])

        people = map.person_container.people
        position = map.person_container.position
        controller = map.person_container.controller
        for person in people:
            pid = person.pid
            self.people[pid] = PerSpr(person, scale=1, size=size, pos=position[pid],
                                      controller=controller[pid], bk_color=(220,220,220))
            self.people[pid].moved = not map.person_container.movable[pid]

            self.person_layer.add(self.people[pid])
            self.cells[position[pid]].person_on = pid

        self.menulayer = menulayer
        self.infolayer = infolayer

        self.board = Board(self.windowsize[0], self.windowsize[1],25,-3)
        self._update = (0, 0)
        self.schedule(self.update)

        self._clear_map()
        self.position = (0, 0)

        print('loaded turn %s' % self.map.turn)
        print('loaded map reconstruct ', self.map.reconstruct_log)


    # callback functions
    def _getitem(self, **kwargs):
        person = kwargs['defeat']
        item = kwargs['item']
        self.add(Getitem(person, item, self.map.global_vars.flags['Have Transporter'],
                         self.map, callback=self._clear))

    def _trans(self, **kwargs):
        pid, pos = kwargs['transtuple']
        target = self.people[pid]
        action = self._transfer(pos, 1)
        map = self.map
        self.cells[map.person_container.position[pid]].person_on = None
        map.person_container.position[pid] = pos
        self.people[pid].pos = pos
        self.cells[pos].person_on = pid
        target.do(action + CallFunc(self._clear))

    def _clear(self, **kwargs):
        # handle the default execute after battle or a movement
        self.get_next_to_delete()

    def _clear_map(self):
        # should be executed after movement and before battle display
        self.state = 'default' #type:
        self.selected = None
        self.target = None
        self.mouse_pos = None
        self.mouse_btn = 0
        self.item = None
        self.sup_dict = None
        self._reset_person = {}
        self.menulayer.disapper()
        self.iter = iter(self.people)
        self.item_w = None
        self.avl = None
        self.excpid = None
        self.allow_cancel = True
        self.transtuple = None
        self.dialog_info = {}
        try:
            self.infolayer.remove(self.info)
            self.remove(self.wpinfo)
        except:
            pass

        self._mapstate = self.map.send_mapstate()
        for cell in self.cells.values():
            cell.state = 'default'
        for person in self.people.values(): #type:PerSpr
            if not person.moved:
                person.state = 'unmoved'
            else:
                person.state = 'moved'
            person.update_hp()

        self.position = (0, 0)
        self._repaint()

    def on_return(self, person, getitem=None, transtuple=None, finish=None, defeat=None):
        if getitem is not None:
            self.add(Getitem(person,getitem,self.map.global_vars.flags['Have Transporter'],
                             self.map, callback=self.end_getitem))
        else:
            if transtuple is not None:
                self.transtuple = transtuple
            if self.transtuple is not None:
                pid, pos = self.transtuple
                target = self.people[pid]
                action = self._transfer(pos,1)
                map = self.map
                self.cells[map.person_container.position[pid]].person_on = None
                map.person_container.position[pid] = pos
                self.people[pid].pos = pos
                self.cells[pos].person_on = pid
                target.do(action + CallFunc(self.clear))
                director.window.push_handlers(self)
            else:
                if finish is not None:
                    _type, _id, _pid = finish[0].split('/')
                    if _pid is 'E':
                        _pid = defeat
                    if _type is 'I':
                        self.add(Getitem(self.people[_pid].person, self.map.global_vars.itemBank[int(_id)],
                                         self.map.global_vars.flags['Have Transporter'], self.map, callback=self.end_getitem))
                        
                    pass
                else:
                    self.clear()

    def set_target(self, value):
        self._target = value
        w = self.windowsize[0]
        if value is not None:
            if value[0] < self.w // 2:
                self.menulayer.menu_back.position = w - w //4, 0
            else:
                self.menulayer.menu_back.position = 0, 0

    def get_target(self):
        return self._target

    target = property(get_target, set_target)

    def focus(self, pid, set=True):
        if not pid in self.people:
            i=0
            j=0
        else:
            i, j = self.people[pid].pos
        x, y = coordinate(i, j, self.size)
        dis_x, dis_y = self.windowsize[0] // 2, self.windowsize[1] // 2
        if x < dis_x:
            x = dis_x
        elif x > self.width + self.size - dis_x:
            x = self.width + self.size - dis_x
        if y < dis_y:
            y = dis_y
        elif y > self.height - dis_y:
            y = self.height - dis_y
        _position = -x + self.windowsize[0] // 2, -y + self.windowsize[1] // 2
        if set:
            self.position = _position
        else:
            return _position

    def next_round(self):
        self.map.turn += 1
        # if self.map.turn > 20:
        #     director.pop()
        self.set_turn(self.map.turn)
        self.map.controller = 0
        self._mapstate = self.map.send_mapstate()
        self.execute_turn_event(callback_func=self.player_phase)

    def update_person(self, i=0):
        if i < self.person_num:
            p = self.person_list[i]
            p.state = 'unmoved'
            p.moved = False
            log = self.map.refresh_person(p.pid)
            prop = p.update_hp(False)
            obj, action = p.set_angle_action(prop, min_duration=0, max_duration=2)
            obj.do(CallFunc(self.focus, p.pid) + action + CallFunc(self.update_person, i+1))
        else:
            self.player_turn()

    def player_turn(self, **kwargs):

        self.focus('1')
        self._clear_map()
        director.window.push_handlers(self)
        print('player_turn push_handlers')
        # before executed, handlers should be removed

    def ai_turn(self, **kwargs):
        if 'Reinforce' in kwargs.keys() and len(kwargs['Reinforce']) > 0:
            events = kwargs['Reinforce']
            self._reinforce(events, callback=self.map.ai_turn2, arena=self)
        else:
            self.map.ai_turn2(self)

    def player_phase(self, **kwargs):
        self.person_list = list(self.people.values())
        self.person_num = len(self.person_list)
        self.update_person()
        pass

    def ai_phase(self):
        self.execute_turn_event(callback_func=self.ai_turn)
        pass

    def execute_turn_event(self, i=0, callback_func=None, **kwargs):

        if i < self.turn_length:
            event = self.turn_event[i]
            if (event['Side'] is None or self.map.controller == event['Side']) \
                and (event['Turn'] is None or self.map.turn == event['Turn']) \
                    and check_condition(event['Condition'], self.map):
                    if 'Reconstruct' in event.keys():
                        self.reconstruct(event['Reconstruct'])
                    self.eventdisplay(
                        event=event, map=self.map,
                        dialog_type=event['Text_type'], dialog_info=self.dialog_info,
                        w=self.windowsize[0], h=self.windowsize[1],
                        callback=self.execute_turn_event, i=i+1,
                        callback_func=callback_func, **kwargs
                    )
            else:
                self.execute_turn_event(i + 1, callback_func, **kwargs)
        else:
            callback_func.__call__(**kwargs)

    def _sequential_move(self, dst):
        # move person of pid through the trace dst
        # at start of this period, remove handlers to avoid events
        action = CallFunc(self.menulayer.disapper)
        for x,y in dst:
            action = action + MoveTo(coordinate(x, y, self.size), 0.5)
        return action

    def _set_moved(self, pid, dst):
        map = self.map
        self.cells[map.person_container.position[pid]].person_on = None
        map.person_container.position[pid] = dst[-1]
        map.person_container.movable[pid] = False
        self.people[pid].state = 'moved'
        self.people[pid].moved = True
        self.people[pid].pos = dst[-1]
        self.cells[dst[-1]].person_on = pid
        self.focus(pid)

    def _transfer(self, pos, duration=2):
        x, y = pos
        action = FadeOut(duration) + Delay(0.5) + \
                 Place(coordinate(x, y, self.size)) + FadeIn(duration)
        return action

    def _reinforce(self, events, callback, **kwargs):
        people = self.map.global_vars.personBank
        position = self.map.person_container.position
        controller = self.map.person_container.controller
        actionlist = []
        for event in events:
            _, pid, clr, _pos, army, pri, strategy = event
            _str = _pos.split(',')
            pos = int(_str[0]), int(_str[1])
            self.map.reinforce_person(pid, int(clr), pos, army, int(pri), strategy)
            person = people[pid]
            self.people[pid] = PerSpr(person, 1, self.size, position[pid],
                                      controller[pid], bk_color=(220, 220, 220))
            self.person_layer.add(self.people[pid])
            self.focus(pid)
            self.cells[position[pid]].person_on = pid
            actionlist.append((self.people[pid], CallFunc(self.focus, pid) + FadeIn(1.5)))
        self._repaint()
        actionlist.append((self, CallFunc(callback.__call__, **kwargs)))
        Sequencial(actionlist).excute()

    def _repaint(self):
        for cell in self.cells.values():
            cell.color = mapstate2color[cell.state]
            cell.opacity = opacity[cell.state]
        for person in self.people.values(): #type:Charactor
            person.inner.color = per_state2color(person.state, person.controller)

        # according to the state of every sprite within, repaint them in the correct color
        pass

    def _in_arena(self, i, j):
        if i < self.w and j < self.h and i >= 0 and j >= 0:
            return True
        else:
            return False

    def on_mouse_motion(self, x, y, buttons, modifiers):
        # use _repaint
        pos = self._coordinate(x, y)
        x1, y1 = self.board.get_dir(x, y)

        self._update = x1, y1
        i, j = self.coordinate_t(x, y)
        if self._in_arena(i, j):
            self._repaint()
            cell = self.cells[(i, j)]
            cell.color = mapstate2color_motion[cell.state]
            cell.opacity = opacity[cell.state]
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        # according to the state link to correct function
        print(self.state)
        self.mouse_pos = self.coordinate_t(x, y)
        self.mouse_btn = buttons
        self._state_control[self.state].__call__()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        # if scroll_y == 1.0:
        #     self.scale = self.scale * 1.1
        # else:
        #     self.scale = self.scale * 0.9
        pass

    def _reset(self):
        # reset to last state
        # specificlly handle with choose_attack
        if self.state is 'choose_attack':
            self.infolayer.remove(self.wpinfo)
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

            self.item = None
        elif self.state is 'choose_door':
            self.menu = Ordermenu(self)
            self.add_menu(self.menu)
            for (i, j) in self.cells.keys():
                cell = self.cells[(i, j)]
                pid = self.selected
                valid = self._mapstate[0]
                if cell.state is 'door':
                    if (i, j) in valid[pid]:
                        cell.state = 'in_self_moverange'
                    else:
                        cell.state = 'default'
        elif self.state in['choose_support', 'choose_exchange', 'choose_steal', 'choose_talk']:
            for pid in self._reset_person.keys():
                self.people[pid].state = self._reset_person[pid]
            '''
            elif self.state is 'choose_exchange':
                for pid in self.exc:
                    self.people[pid].state = self._reset_person[pid]
            elif self.state is 'choose_steal':
                for pid in self.stl_dict:
                    self.people[pid].state = self._reset_person[pid]
            elif self.state is 'choose_talk':
                for pid in self.talk_dict:
                    self.people[pid].state = self._reset_person[pid]
            '''
            self.menu = Ordermenu(self)
            self.add_menu(self.menu)

        elif self.state in ['wand_type0','wand_type1','wand_type2','wand_type3',
                            'wand_type4', 'wand_type5', 'wand_type6', 'wand_type7_confirm',
                            'wand_type8', 'wand_type9']:
            self.wand(self.avl)
            pid = self.selected
            valid = self._mapstate[0]
            for (i, j) in self.cells.keys():
                cell = self.cells[(i, j)]
                if cell.state is 'in_self_wandrange':
                    if (i, j) in valid[pid]:
                        cell.state = 'in_self_moverange'
                    else:
                        cell.state = 'default'
            self.item = None
        self.state = 'valid_dst'
        self._repaint()
        pass

    def _set_state(self, state):
        self.state = state

    def add_menu(self, menu, dt=0.2):
        self.menulayer.appear()
        director.window.remove_handlers(self)
        self.do(Delay(dt) + CallFunc(self.menulayer.add, menu))

    def set_pos(self, menu):
        menu.position = self.menulayer.menu_back.position

    def _set_areastate(self, area, state):
        for i, j in area:
            self.cells[(i, j)].state = state
        self._repaint()

    def _push_scene(self, layer, callback=None, **kwargs):
        if callback is None:
            callback_func = self._clear
        else:
            callback_func = callback
        scene = Scene((layer(self, self.windowsize[0], self.windowsize[1],
                             callback=callback_func, **kwargs)))
        director.push(FadeTransition(scene, duration=1.5))

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
            'choose_support': self._choose_support, 8: self._choose_support,
            'end_turn': self._end_turn, 9: self._end_turn,
            'wand_type0': self._wand_type0,10:self._wand_type0,
            'wand_type1': self._wand_type1,
            'wand_type1_confirm': self._wand_type1_confirm,
            'wand_type2': self._wand_type2,
            'wand_type3': self._wand_type3,
            'wand_type3_confirm': self._wand_type3_confirm,
            'wand_type4':self._wand_type4,
            'wand_type5': self._wand_type5,
            'wand_type5_chstar': self._wand_type5_chstar,
            'wand_type5_confirm': self._wand_type5_confirm,
            'wand_type6': self._wand_type6,
            'wand_type7': self._wand_type7,
            'wand_type7_confirm': self._wand_type7_confirm,
            'wand_type8': self._wand_type8,
            'choose_exchange': self._choose_exchange,
            'choose_steal': self._choose_steal,
            'choose_door': self._choose_door,
            'choose_talk': self._choose_talk,
        }

    def _callback(self, **kwargs):
        director.window.push_handlers(self)
        print('callback push_handlers')
        self.state = 'default'

    def _default(self):
        # 0   default
        # not any army is selected.
        # event handler should be true to wait for commands
        # consider end_turn only under this state
        if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
            return
        if self.mouse_btn == 1:
            if self.cells[self.mouse_pos].person_on is not None: # just select a person
                pid = self.cells[self.mouse_pos].person_on
                self.people[pid].state = 'selected'
                self.selected = pid
                self.origin_pos = self.mouse_pos
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
        elif self.mouse_btn == 4:
            if self.cells[self.mouse_pos].person_on is not None:
                pid = self.cells[self.mouse_pos].person_on
                select = self.people[pid].person
                director.window.remove_handlers(self)
                self.info = Personinfo(select, callback=self._callback)
                self.infolayer.add(self.info)
                self.state = 'person_info'
            else:
                self.end = Endturn(self)
                self.add_menu(self.end)
                self.state = 'end_turn'
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
                self.add_menu(self.menu)
                self.state = 'valid_dst'
                self.cells[self.target].person_on = self.selected
                self.cells[self.origin_pos].person_on = None
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
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_attackrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is 1:
                self.menulayer.disapper()
                self.infolayer.remove(self.wpinfo)
                at = self.people[self.selected].person
                df = self.people[cell.person_on].person
                wp = self.item
                self.info = Battleinfo(at, df, wp, self.map, self.target)
                self.battlelist = [at, df, wp, self.map, self.target]
                self.infolayer.add(self.info)
                self.state = 'confirm_attack'
            else:
                self._reset()
            pass
        pass

    def _confirm_attack(self):
        # 6   confirm_attack
        # showing battle_simulate info
        # if confirm, push battle scene and then return to 1, else turn to 5
        self.infolayer.remove(self.info)
        if self.mouse_btn is 4:
            self.state = 'choose_attack'
            self.infolayer.add(self.wpinfo)
        elif self.mouse_btn is 1:
            self.attacking()
            pass

    def _show_battle_result(self):
        # 7   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5
        self.get_next_to_delete()
        self.get_next_event()

    def _choose_support(self):
        # 8   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5
        if self.mouse_btn is 1:
            if self.mouse_pos in self.sup_dict.values():
                director.window.remove_handlers(self)
                self.textlist = self.map.build_support(self.selected, self.cells[self.mouse_pos].person_on)
                for pid in self.sup_dict:
                    self.people[pid].state = self._reset_person[pid]
                dst = self._mapstate[0][self.selected][self.target][1]
                pid = self.selected
                obj = self.people[pid]
                action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + CallFunc(self._clear_map)
                if len(self.textlist) > 0:
                    action = action + CallFunc(self._push_scene, Dialogscene)
                obj.do(action)
        elif self.mouse_btn is 4:
            self._reset()
        pass

    def _end_turn(self):
        # 9   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5
        if self.mouse_btn == 4:
            try:
                self.menulayer.remove(self.end)
                self.menulayer.disapper()
            except:
                pass
            self.state = 'default'
            del self.end

    def _wand_type0(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is not 1:
                user = self.people[self.selected].person
                target = self.people[cell.person_on].person
                wand = self.item_w
                self.wandlist_type0 = [user, wand, target, self.map]
                self._battle(Wandtype0)
            else:
                self._reset()
            pass
        pass

    def _wand_type1(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is 1:
                user = self.people[self.selected].person
                target = self.people[cell.person_on].person
                wand = self.item_w
                self.wandlist_type1 = [user, wand, target, self.map, self.target]
                hitr = Type1(user, wand, target, self.map, self.target).simulate()
                self.hitrate = Info()
                self.add(self.hitrate)
                self.hitrate.display([str(hitr)])
                self.state = 'wand_type1_confirm'
            else:
                self._reset()
            pass
        pass

    def _wand_type1_confirm(self):
        self.remove(self.hitrate)
        if self.mouse_btn is 1:
            self._battle(Wandtype1)
        else:
            self.state = 'wand_type1'
            pass
        pass

    def _wand_type2(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is not 1:
                user = self.people[self.selected].person
                target = self.people[cell.person_on].person
                wand = self.item_w
                self.wandlist_type2 = [user, wand, target, self.map]
                self.add_menu(Listwand(target.item, self, type=2))
            else:
                self._reset()
            pass
        pass

    def _wand_type3(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is 1:
                user = self.people[self.selected].person
                target = self.people[cell.person_on].person
                wand = self.item_w
                self.wandlist_type3 = [user, wand, target, self.map, self.target]
                eqp=target.get_equip()
                target_item_list=target.item.copy()
                if not eqp==None:
                    target_item_list.remove(eqp)
                self.add_menu(Listwand(target_item_list, self, type=3))
            else:
                self._reset()
            pass
        pass

    def _wand_type3_confirm(self):
        self.remove(self.hitrate)
        if self.mouse_btn is 1:
            self._battle(Wandtype3)
        else:
            self.wandlist_type3.pop()
            self.state = 'wand_type3'
            target = self.wandlist_type3[2]
            eqp = target.get_equip()
            target_item_list = target.item.copy()
            if not eqp == None:
                target_item_list.remove(eqp)
            self.add_menu(Listwand(target_item_list, self, type=3))
            pass
        pass

    def _wand_type4(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is None:
                user = self.people[self.selected].person
                target = self.mouse_pos
                wand = self.item_w
                self.wandlist_type4 = [user, wand, target, self.map]
                self._battle(Wandtype4)
            else:
                self._reset()
            pass
        pass

    def _wand_type5(self):
        '''
        wait for choose an enemy
        :return:
        '''
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None \
                    and self.people[cell.person_on].controller is 1:
                self.state = 'wand_type5_chstar'
                self.objper = self.people[cell.person_on].person
            else:
                self._reset()
            pass
        pass

    def _wand_type5_chstar(self):
        if self.mouse_btn == 4:
            self.state = 'wand_type5'
        elif self.mouse_btn == 1:
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is None:
                user = self.people[self.selected].person
                target = self.objper
                wand = self.item_w
                self.wandlist_type5 = [user, wand, target, self.map, self.target, self.mouse_pos]
                hitr = Type5(user, wand, target, self.map, self.target, self.mouse_pos).simulate()
                self.hitrate = Info()
                self.add(self.hitrate)
                self.hitrate.display([str(hitr)])
                self.state = 'wand_type5_confirm'

    def _wand_type5_confirm(self):
        self.remove(self.hitrate)
        if self.mouse_btn is 1:
            dst = self._mapstate[0][self.selected][self.target][1]
            Sequencial(
                [(self.people[self.selected], self._sequential_move(dst)),
                (self.people[self.selected], CallFunc(self._set_moved, self.selected, dst)),
                (self.people[self.selected], CallFunc(self._clear_map)),
                (self.people[self.selected], CallFunc(self._push_scene, Wandtype5))]
            ).excute()
            '''Graphic(
                (self.people[self.selected],
                 self._sequential_move(self.selected, self._mapstate[0][self.selected][self.target][1]), set()),
                (self.people[self.objper.pid], self._transfer(self.objper.pid, self.wandlist_type5[-1]), set([0])),
                (self, CallFunc(self._push_scene, Wandtype5), set([1])),
                (self, CallFunc(self._clear_map), set([2])),
                (self, CallFunc(self._set_state, 'show_battle_result'), set([3]))
            ).excute()'''

        else:
            self.state = 'wand_type5'
            pass
        pass

    def _wand_type6(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is not None\
                and self.people[cell.person_on].controller is not 1:
                user = self.people[self.selected].person
                target = self.people[cell.person_on].person
                wand = self.item_w
                self.wandlist_type6 = [user, wand, target, self.map, self.target]
                self._battle(Wandtype6)
            else:
                self._reset()
            pass
        pass

    def _wand_type7(self):
        if self.mouse_btn == 4:
            for pid in self._reset_person:
                self.people[pid].state = self._reset_person[pid]
            self.wand(self.avl)
            self._repaint()
        elif self.mouse_btn == 1:
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
                return
            cell = self.cells[self.mouse_pos]

            if cell.person_on is not None:
                pid = cell.person_on
                if self.people[pid].state is 'can_wanduse':
                    self.state = 'wand_type7_confirm'
                    self.objper = self.people[cell.person_on].person
                    item_w = self.item_w
                    max_range = item_w.itemtype.max_range
                    min_range = item_w.itemtype.min_range
                    if max_range == -1:
                        person = self.people[self.selected].person
                        max_range = max(1, person.ability['MGC'])
                    i, j = self.target
                    area = []
                    for distance in range(min_range, max_range + 1):
                        for dx in range(distance + 1):
                            dy = distance - dx
                            for x, y in [(i + dx, j + dy), (i + dx, j - dy), (i - dx, j + dy), (i - dx, j - dy)]:
                                if x in range(self.w) and y in range(self.h):
                                    area.append((x, y))
                    self._set_areastate(area, 'in_self_wandrange')

            else:
                for pid in self._reset_person:
                    self.people[pid].state = self._reset_person[pid]
                self.wand(self.avl)
                self._repaint()
            pass
        pass

    def _wand_type7_confirm(self):
        if self.mouse_btn == 4:
            self.state = 'wand_type7'
        elif self.mouse_btn == 1:
            cell = self.cells[self.mouse_pos]
            if cell.state is 'in_self_wandrange' and cell.person_on is None:
                user = self.people[self.selected].person
                target = self.objper
                wand = self.item_w
                self.wandlist_type7 = [user, wand, target, self.map, self.mouse_pos]
                dst = self._mapstate[0][self.selected][self.target][1]
                Sequencial(
                    [(self.people[self.selected], self._sequential_move(dst)),
                    (self.people[self.selected], CallFunc(self._set_moved, self.selected, dst)),
                    (self.people[self.selected], CallFunc(self._clear_map)),
                    (self.people[self.selected], CallFunc(self._push_scene, Wandtype7))]
                ).excute()
        pass

    def _wand_type8(self):
        if self.mouse_btn == 4:
            self._reset()
        elif self.mouse_btn == 1:
            user = self.people[self.selected].person
            wand = self.item_w
            self.wandlist_type8 = [user, wand, self.map, self.target]
            self._battle(Wandtype8)
            pass
        pass

    def _choose_exchange(self):
        if self.mouse_btn == 4:
            self._reset()
            pass
        elif self.mouse_btn == 1:
            pid = self.cells[self.mouse_pos].person_on
            if pid is not None and pid in self.exc:
                director.window.remove_handlers(self)
                self.menulayer.add(Weaponexchange(self.people[self.selected].person.item, self,
                                                  (-self.windowsize[0], 0)), name='left')
                self.menulayer.add(Weaponexchange(self.people[pid].person.item, self,
                                                  (-self.windowsize[0]//2, 0)), name='right')
                self.excpid = pid
            pass

    def _choose_steal(self):
        if self.mouse_btn == 4:
            self._reset()
            pass
        elif self.mouse_btn == 1:
            pid = self.cells[self.mouse_pos].person_on
            if pid in self.stl_dict:
                director.window.remove_handlers(self)
                can_steal = self.stl_dict[pid]
                self.stl_obj = pid
                self.add_menu(Liststeal(self, can_steal, self.exe_steal))
                self.menulayer.disapper()
            else:
                self._reset()
            pass

    def _choose_door(self):
        if self.mouse_btn == 4:
            self._reset()
            pass
        elif self.mouse_btn == 1:
            if self.mouse_pos in self._doors.keys():
                director.window.remove_handlers(self)
                item = self._key
                pid = self.selected
                act_obj = self.people[pid]
                person = act_obj.person
                if item is not None:
                    item.use -= 1
                    if item.use == 0:
                        person.banish(item)
                event = self._doors[self.mouse_pos]
                dst = self._mapstate[0][self.selected][self.target][1]
                action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + CallFunc(
                    self._clear_map)
                act_obj.do(action + CallFunc(self.reconstruct, event['Reconstruct']) +
                           CallFunc(self.eventdisplay, event=event, map=self.map,
                                  dialog_type=None, dialog_info=self.dialog_info,
                                  w=self.windowsize[0], h=self.windowsize[1],
                                  callback=self._clear))
            else:
                self._reset()
            pass

    def _choose_talk(self):
        if self.mouse_btn == 4:
            self._reset()
            pass
        elif self.mouse_btn == 1:
            pid = self.cells[self.mouse_pos].person_on
            if pid is not None and pid in self.talk_dict:
                director.window.remove_handlers(self)
                event = self.talk_dict[pid]
                pid = self.selected
                obj = self.people[pid]
                dst = self._mapstate[0][pid][self.target][1]
                action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + \
                         CallFunc(self._clear_map) + Delay(0.1)
                obj.do(action + CallFunc(self.eventdisplay, event=event, map=self.map,
                                         dialog_type='S', dialog_info=self.dialog_info,
                                         w=self.windowsize[0], h=self.windowsize[1],
                                         callback=self._clear))

            pass

    def get_next_to_delete(self):
        try:
            pid = next(self.iter)
        except:
            self.get_next_event()
            return
        person = self.people[pid].person
        if person.ability['HP'] <= 0:
            self.people[pid].do(FadeOut(2)+CallFunc(self._delete_person, pid))
        else:
            self.get_next_to_delete()
        pass

    def get_next_event(self, i=0, **kwargs):
        if i < self.general_length:
            event = self.general[i]
            if check_condition(event['Condition'], self.map):
                if 'Reconstruct' in event.keys():
                    self.reconstruct(event['Reconstruct'])
                self.eventdisplay(
                    event=event, map=self.map,
                    dialog_type=event['Text_type'], dialog_info=self.dialog_info,
                    w=self.windowsize[0], h=self.windowsize[1],
                    callback=self.get_next_event, i=i+1
                )
            else:
                self.get_next_event(i+1)
        else:
            self.map.take_turn(self)
            pass


    def _battle(self, layer, **kwargs):
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) +\
                 CallFunc(self._clear_map) + CallFunc(self._push_scene, layer, **kwargs)
        obj = self.people[pid]
        obj.do(action)

    def _delete_person(self, pid):
        person = self.people[pid]
        pos = self.people[pid].pos
        self.people.pop(pid)
        self.cells[pos].person_on = None
        self.person_layer.remove(person)
        del person
        self.get_next_to_delete()

    def select_target(self, item, info):
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
        self.wpinfo = info
        self.infolayer.add(info)
        director.window.push_handlers(self)

    def support(self, sup_dict):
        director.window.push_handlers(self)
        self.state = 'choose_support'
        for pid in sup_dict:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_support'
        self.sup_dict = sup_dict
        self._repaint()

    def wanduse(self, item_w):
        self.menulayer.disapper()
        area = []
        max_range = item_w.itemtype.max_range
        min_range = item_w.itemtype.min_range
        if max_range == -1:
            person = self.people[self.selected].person
            max_range = max(1, person.ability['MGC'])
        (i, j) = self.target
        wandtype = item_w.itemtype.wand['Type']
        if wandtype == 7:
            for _x, _y in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                x, y = i + _x, j + _y
                if self._in_arena(x, y) and self.cells[(x, y)].person_on is not None:
                    pid = self.cells[(x, y)].person_on
                    if self.people[pid].controller is not 1:
                        self._reset_person[pid] = self.people[pid].state
                        self.people[pid].state = 'can_wanduse'
            self._repaint()
        else:
            for distance in range(min_range, max_range + 1):
                for dx in range(distance + 1):
                    dy = distance - dx
                    for x, y in [(i + dx, j + dy), (i + dx, j - dy), (i - dx, j + dy), (i - dx, j - dy)]:
                        if x in range(self.w) and y in range(self.h):
                            area.append((x, y))
            self._set_areastate(area, 'in_self_wandrange')
        self.item_w = item_w
        director.window.push_handlers(self)

        if wandtype is not None:
            if wandtype == 8:
                user = self.people[self.selected].person
                wand = self.item_w
                self.wandlist_type8 = [user, wand, self.map, self.target]
                director.window.remove_handlers(self)
                self._battle(Wandtype8)
            else:
                self.state = 'wand_type' + str(wandtype)
        else:
            self.add_menu(Showwand(self.avl, self))
        '''if item_w.itemtype.wand['Type'] == 0:
            self.state = 'wand_type0'
        elif item_w.itemtype.wand['Type'] == 1:
            self.state = 'wand_type1'
        elif item_w.itemtype.wand['Type'] == 2:
            self.state = 'wand_type2'
        elif item_w.itemtype.wand['Type'] == 3:
            self.state = 'wand_type3'
        elif item_w.itemtype.name == 'Rewarp':
            self.state = 'wand_type4_rewarp'
        '''

    def attacking(self, **kwargs):
        director.window.remove_handlers(self)
        if 'pid' not in kwargs:
            # this is from self movements
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
        else:
            # from ai movements
            pid = kwargs['pid']
            dst = kwargs['dst']
            rng = kwargs['rng']
            self.battlelist = kwargs['battlelist']
            self._set_areastate(rng, 'in_enemy_moverange')
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) \
                 + CallFunc(self._clear_map) + CallFunc(self._push_scene, Battlescene, callback=self._clear)
        obj = self.people[pid]
        obj.do(action)

    def attack(self):
        print('attack push_handlers')
        self._set_areastate([self.target], 'target')
        items = self.people[self.selected].person.item
        self.add_menu(Weaponmenu(items, self.map, self))
        pass

    def item_show(self):
        self._set_areastate([self.target], 'target')
        items = self.people[self.selected].person.item
        self.add_menu(Showweapon(items, self))
        pass

    def end_turn(self):
        self._clear_map()
        self.map.controller = 1
        self.map.reset_state(0)
        director.window.remove_handlers(self)
        self.execute_turn_event(callback_func=self.ai_turn)

    def flag(self):
        self.menulayer.disapper()
        flags = self.map.global_vars.flags
        for item in flags:
            print(item, flags[item])
        self.state = 'default'
        director.window.push_handlers(self)

    def move(self, **kwargs):
        director.window.remove_handlers(self)
        if len(kwargs) is 0:
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
        else:
            pid = kwargs['pid']
            dst = kwargs['dst']
            rng = kwargs['rng']
            self._set_areastate(rng, 'in_enemy_moverange')
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + \
                 CallFunc(self._clear_map) + CallFunc(self._clear)
        obj = self.people[pid]
        obj.do(action)
        pass

    def wand(self, avl):
        director.window.push_handlers(self)
        self._set_areastate([self.target], 'target')
        self.add_menu(Showwand(avl, self))
        self.avl = avl

    def cancel(self):
        director.window.push_handlers(self)
        self._set_areastate([self.target], 'in_self_moverange')
        self.state = 'valid_select'
        self.menulayer.disapper()
        self.cells[self.target].person_on = None
        self.cells[self.origin_pos].person_on = self.selected
        self.target = None

    def save(self):
        director.window.push_handlers(self)
        self.menulayer.disapper()
        self.state = 'default'
        self.map.map_save()

    def load(self):
        map = self.map.map_load()[0] #type:map_controller.Main
        menulayer = Menulayer()
        infolayer = Layer()
        arena = Arena(map, menulayer, infolayer, self.size)
        class Transition(FadeTransition):
            def finish(self):
                super().finish()
                for rec in map.reconstruct_log:
                    arena.reconstruct(rec, ty='load')
                arena.map.take_turn(arena)

        director.replace(Transition(Scene(arena, menulayer, infolayer), duration=1))
        self.kill()
        del self

    def cancel_select(self):
        self.state = 'valid_dst'
        for pid in self.stl_dict:
            self.people[pid].state = self._reset_person[pid]
        self._repaint()
        self.add_menu(Ordermenu(self))

    def use(self, item):
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        person = self.people[pid].person
        obj = self.people[pid]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst)
        use_effect = person.use_item(item)
        if 'PROMOTE' in use_effect:
            promote_cls_list = person.can_promote(self.map.global_vars)
            self.menulayer.add(Listcls(promote_cls_list, self.promote, action=action, pid=pid))
            pass
        else:
            obj.do(action + CallFunc(self._clear_map)+ CallFunc(self.map.take_turn, self))
        pass

    def promote(self, cls, pid, action):
        person = self.people[pid].person
        obj = self.people[pid]
        promote_bonus, abl_ori = person.promote(cls, self.map.global_vars)
        def _act(self):
            director.window.remove_handlers(self)
            self.add(Experience2(promote_bonus, abl_ori, self._clear_map))

        obj.do(action + CallFunc(_act, self))

    def equip(self, item):
        pid = self.selected
        person = self.people[pid].person
        person.equip(item)
        self.item_show()

    def banish(self, item):
        pid = self.selected
        person = self.people[pid].person
        person.banish(item)
        self.item_show()

    def seize(self, event):
        director.window.remove_handlers(self)
        pid = self.selected
        obj = self.people[pid]
        dst = self._mapstate[0][self.selected][self.target][1]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + CallFunc(self._clear_map)
        obj.do(action +  CallFunc(self.eventdisplay, event=event, map=self.map,
                                 dialog_type='M', dialog_info=self.dialog_info,
                                 w=self.windowsize[0], h=self.windowsize[1],
                                 callback=self._clear))


    def set_turn(self, turn):
        # change the turn over the arena
        pass

    def can_exchange(self, pos):
        exc_obj = []
        for (x, y) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            i, j = pos[0]+x, pos[1]+y
            if self._in_arena(i, j):
                pid = self.cells[(i, j)].person_on
                if pid is not None:
                    if self.map.person_container.controller[pid] == 0:
                        exc_obj.append(pid)
        return exc_obj

    def exchange(self, exc):
        director.window.push_handlers(self)
        self._set_areastate([self.target], 'target')
        self.state = 'choose_exchange'
        for pid in exc:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_exchange'
        self.exc = exc
        self._repaint()
        self.menulayer.disapper()

    def exchange_item(self, item1, item2, name=None):
        print(item1, item2)
        if name is None:
            pid1, pid2 = self.selected, self.excpid
        elif name is 'left':
            pid1 = pid2 = self.selected
        elif name is 'right':
            pid1 = pid2 = self.excpid
        else:
            return
        self.map.exchange_item(pid1, pid2, item1, item2)
        self.menulayer.add(Weaponexchange(self.people[self.selected].person.item, self,
                                          (-self.windowsize[0], 0)), name='left')
        self.menulayer.add(Weaponexchange(self.people[self.excpid].person.item, self,
                                          (-self.windowsize[0]//2, 0)), name='right')

        self.allow_cancel = False

    def wandrpr(self, item):
        director.window.push_handlers(self)
        self.wandlist_type2.append(item)
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst)\
                 + CallFunc(self._push_scene, Wandtype2)
        obj = self.people[pid]
        obj.do(action)

    def wandstl(self, item):
        director.window.push_handlers(self)
        self.wandlist_type3.append(item)
        self.state = 'wand_type3_confirm'
        user, wand, target, self.map, self.target, _ = self.wandlist_type3
        hitr_3 = Type3(user, wand, target, self.map, self.target, item).simulate()
        self.hitrate = Info()
        self.add(self.hitrate)
        self.hitrate.display([str(hitr_3)])

    def exe_steal(self, item):
        obj = self.people[self.stl_obj].person #type:person.Person
        obj.dequip(item)
        obj.item.remove(item)
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + CallFunc(self._clear_map)
        act_obj = self.people[pid]
        act_per = act_obj.person
        act_obj.do(action + CallFunc(self.on_return, person=act_per, getitem=item))

    def visit_village(self, event):
        director.window.remove_handlers(self)
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst)
        obj = self.people[pid]
        self.textlist = event['Text']
        self.dialog_info['V'] = obj.person
        _event = Eventdisplay(event=event,
                              map=self.map,
                              dialog_type='S',
                              dialog_info=self.dialog_info,
                              w=self.windowsize[0],
                              h=self.windowsize[1],
                              callback=self._clear)
        self.add(_event)
        obj.do(action + CallFunc(_event.display))

    def treasury(self, event, item):
        pid = self.selected
        person = self.people[pid].person
        dst = self._mapstate[0][self.selected][self.target][1]

        action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) \
                 + CallFunc(self._clear_map)

        obj = self.people[pid]
        if item is not None:
            if item.itemtype.infinite is not -1:
                item.use -= 1
                if item.use < 1:
                    person.banish(item)
            self.dialog_info['V'] = obj.person
            if 'Reconstruct' in event.keys():
                action = action + CallFunc(self.reconstruct, event['Reconstruct'])
            obj.do(action + CallFunc(self.eventdisplay, event=event, map=self.map,
                                  dialog_type=None, dialog_info=self.dialog_info,
                                  w=self.windowsize[0], h=self.windowsize[1],
                                  callback=self._clear))
            pass
        else:
            obj.do(action)

    def steal(self, stl_dict):
        director.window.push_handlers(self)
        self.state = 'choose_steal'
        for pid in stl_dict:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_steal'
        self.stl_dict = stl_dict
        self._repaint()
        pass

    def doors(self, doors, key):
        director.window.push_handlers(self)
        self.state = 'choose_door'
        self._set_areastate(doors, 'door')
        self._doors = doors
        self._key = key

    def talk(self, talk_dict):
        director.window.push_handlers(self)
        self.state = 'choose_talk'
        for pid in talk_dict:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_talk'
        self.talk_dict = talk_dict
        self._repaint()

    def eventdisplay(self, callback=None, **kwargs):
        self.position = (0, 0)
        display = Eventdisplay(callback=callback, **kwargs)
        self.add(display)
        display.display()

    def reconstruct(self, rec, ty='default'):
        if rec is not None:
            if ty is 'default':
                self.map.reconstruct_log.append(rec)
            if type(rec) is str:
                path = os.getcwd()[:-3] + "data\\"
                _rec = json.load(open(path + rec, "r"))
            else:
                _rec = rec
            self.map.map_reconstruct(_rec)
            x, y, m, n = _rec["Anchor_X"], _rec["Anchor_Y"], _rec["M"], _rec["N"]
            width, height = m * self.size, n * self.size
            _x, _y = (x * 2 + m - 1) / 2, (y * 2 + n - 1) / 2
            recon = Sprite(_rec['Pic'], position=coordinate(_x, _y, self.size))
            recon.scale_x, recon.scale_y = width / recon.width, height / recon.height
            self.remove(self.person_layer)
            self.add(recon)
            self.add(self.person_layer)
        else:
            pass

    def defeated(self):
        center = self.windowsize[0] // 2, self.windowsize[1] // 2
        class Defeatlayer(Layer):
            def __init__(self):
                super().__init__()
                self.position = center
                self.add(Text(text='Defeated', font_size=40))
            def on_mouse_press(self, x, y, buttons, modifiers):
                director.pop()

        layer = Defeatlayer()

        class Transition(FadeTransition):
            def finish(self):
                super().finish()
                director.window.push_handlers(layer)

        director.window.remove_handlers(self)
        director.replace(Transition(Scene(layer)))

    def win(self):
        director.window.remove_handlers(self)
        event = self.map.after
        print(event)
        after = Afterevent(event=event, map=self.map,
                    dialog_type='S', dialog_info=self.dialog_info,
                    w=self.windowsize[0], h=self.windowsize[1],
                    callback=self._next)
        self.add(after)
        x, y = self.position
        after.position = -x, -y
        after.display()

    def _next(self, **kwargs):
        map = self.map.global_vars.new_map(kwargs['Map'])[0]
        menulayer = Menulayer()
        infolayer = Layer()
        arena = Arena(map, menulayer, infolayer, self.size)

        class Transition(FadeTransition):
            def finish(self):
                super().finish()
                for rec in map.reconstruct_log:
                    arena.reconstruct(rec, ty='load')
                arena.map.take_turn(arena)

        director.replace(Transition(Scene(arena, menulayer, infolayer), duration=1))
        self.kill()
        del self

    def remove(self, obj):
        super().remove(obj)
        del obj

    def coordinate_t(self, x, y):
        pos = self._coordinate(x, y)
        i = int(pos[0] // self.size)
        j = int(pos[1] // self.size)
        return i, j

    def update(self, dt):
        x1, y1 = self._update
        x0, y0 = self.position
        if x0 > 0 and x1 > 0 or x0 < -(self.width - self.windowsize[0]) and x0 < 0:
            x1 = 0
        if y0 > 5 and y1 > 0 or y0 < -(self.height - self.windowsize[1]) - 5 and y1 < 0:
            y1 = 0
        self.position = self.position[0] + x1, \
                        self.position[1] + y1

    def _coordinate(self,x, y):
        return ((x - self.anchor_x - self.position[0]) // self.scale + self.anchor_x) ,\
              ((y - self.anchor_y - self.position[1]) // self.scale + self.anchor_y)

class Board():
    def __init__(self, w=800, h=600, margin=20, step=-2):
        self.w = w
        self.h = h
        self.margin = margin
        self.step = step
        self.up = self.h - self.margin
        self.right = self.w - self.margin

    def get_dir(self, x, y):
        if x < self.margin:
            if y < self.margin:
                return (-self.step, -self.step)
            elif y > self.up:
                return (-self.step, self.step)
            else:
                return (-self.step, 0)
        elif x > self.right:
            if y > self.up:
                return (self.step, -self.step)
            elif y < self.margin:
                return (self.step, self.step)
            else:
                return (self.step, 0)
        else:
            if y < self.margin:
                return (0, -self.step)
            elif y > self.up:
                return (0, self.step)
            else:
                return (0, 0)


def map_init():
    data = Data()
    global_vars = Global(data)
    map = global_vars.new_game()
    return map

def coordinate_t(x, y, size):
    i = x // size
    j = y // size
    return i, j

def coordinate(i, j, size):
    x = i * size + size // 2
    y = j * size + size // 2
    return x, y

def new_game(map, size=80):
    menulayer = Menulayer()
    infolayer = Layer()
    arena = Arena(map, menulayer, infolayer, size)

    class Transition(FadeTransition):
        def finish(self):
            super().finish()
            arena.next_round()

    director.push(Transition(Scene(arena, menulayer, infolayer)))

def load_game(map, size=80):
    menulayer = Menulayer()
    infolayer = Layer()
    arena = Arena(map, menulayer, infolayer, size)

    class Transition(FadeTransition):
        def finish(self):
            super().finish()
            for rec in map.reconstruct_log:
                arena.reconstruct(rec, ty='load')
            arena.map.take_turn(arena)

    director.push(Transition(Scene(arena, menulayer, infolayer), duration=1))


if __name__ == '__main__':
    pass






