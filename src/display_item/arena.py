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
from cocos.cocosnode import CocosNode
from cocos.scenes import FadeTransition
from cocos.batch import BatchNode
from .sprite import Charactor, Cell, Cursor
from .state2color import *
from .info import Personinfo, Battleinfo, Experience2
from .menu import *
from .background import Background
from .battle_scene import *
from .ring import PerSpr, Blood
from .animation import Turn, Chapter
from .action_control import Sequencial, Graphic
from .thumb import Thumb
from .saveload import Main as Saveload
from .eventdisplay import *
from .. import map_controller
from ..global_vars import Main as Global
from ..data_loader import Main as Data
from ..person_container import Main as Person_Container
from ..terrain_container import Main as Terrain_Container
from ..wand import Type1, Type3, Type5
from typing import Dict
from pyglet.window import key, mouse

class Arena(Layer):
    """
    the holder of map and items
    """

    is_event_handler = False

    def __init__(self, map, menulayer,infolayer,size=80):
        """

        :param map: the map behind to give instuctions
        :param menulayer: holder for display menus so that they would on the same place of the screen no matter how the arena moves
        :param infolayer: holder for display infos like person info
        :param size: the size of a cell , integer,  size * size
        """
        super(Arena, self).__init__()

        # initialize the holder according to the map
        self.map = map  # type:map_controller.Main
        self.size = size
        self.w, self.h = map.terrain_container.M, map.terrain_container.N
        self.width, self.height = self.w*size, self.h*size
        self.windowsize = director.get_window_size()
        # self.anchor = self.width // 2, self.height // 2


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
        self.person_layer = BatchNode()
        self.cell_layer = BatchNode()
        self.add(self.cell_layer)

        for i in range(self.w):
            for j in range(self.h):
                self.cells[(i, j)] = Cell(size, (i, j))
                self.cell_layer.add(self.cells[(i, j)])

        people = map.person_container.people
        position = map.person_container.position
        controller = map.person_container.controller

        for person in people:
            pid = person.pid
            self.people[pid] = PerSpr(person, scale=1, size=size, pos=position[pid],
                                      controller=controller[pid])
            self.people[pid].moved = not map.person_container.movable[pid]
            self.person_layer.add(self.people[pid])
            self.cells[position[pid]].person_on = pid

        self.add(self.person_layer)
        self.menulayer = menulayer
        self.infolayer = infolayer

        self.board = Board(self.windowsize[0], self.windowsize[1],
                           25,-5)
        self.settings = self.map.global_vars.settings
        self._update = (0, 0)
        self.schedule(self.update)

        self.cursor = Cursor(size)
        self.cell_layer.add(self.cursor)

        self._clear_map()

        print('loaded turn %s' % self.map.turn)
        print('loaded map reconstruct ', self.map.reconstruct_log)
        print('map size %d, %d'% (self.width, self.height))



    def get_settings(self):
        return self._settings

    def set_settings(self, value):
        self._settings = value
        self.board.step = rolling[self._settings['rolling']]
        path = self.map.global_vars.data.get_root('data')
        json.dump(self._settings, open(path+'settings.json', 'w'))

    settings = property(get_settings, set_settings)

    # callback functions

    def _clear(self, **kwargs):
        """
        handle the default execute after battle or a movement
        """
        self.do(Delay(0.5) + CallFunc(self.get_next_to_delete))

    def _clear_map(self):
        """
        should be executed after movement and before battle display
        set state into default
        """
        self.state = 'default' #type:
        self.allow_move = True
        self.selected = None
        self.target = None
        self.mouse_pos = None
        self.mouse_btn = 0
        self.item = None
        self.sup_dict = None
        self._reset_person = {}
        self._reset_cell = {}
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
        self.wpinfo = CocosNode()

        self._mapstate = self.map.send_mapstate()
        for cell in self.cells.values():
            cell.state = 'default'
        for person in self.people.values(): #type:PerSpr
            if not person.moved:
                person.set_default()
            else:
                person.set_moved()
            person.update_hp()
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
                        gititem = Getitem(self.people[_pid].person,
                                          self.map.global_vars.itemBank[int(_id)],
                                         self.map.global_vars.flags['Have Transporter'],
                                          self.map, callback=self.end_getitem)
                        self.add(gititem)
                        gititem.position = -self.position[0], -self.position[1]
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
        """
        this is for the arena to focus a certain person
        :param pid: the person pid to focus
        :param set: if true the arena will focus immediately, else it will return the position for arena to focus
        :return:
        """
        print('%s focus'%pid)
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
        """
        this is the entry of a turn begins
        first show infos of player phase, then execute player phase
        :return:
        """

        self.map.turn += 1
        print(self.map.turn)
        # if self.map.turn > 20:
        #     director.pop()
        self.set_turn(self.map.turn)
        self.map.controller = 0
        self._mapstate = self.map.send_mapstate()
        self.show_infos(turn=self.map.turn, phase='Player Phase', callback=self.player_phase, reset=True)

    def _residual(self, obj, callback, **kwargs):
        self.infolayer.remove(obj)
        self.visible = True
        self.execute_turn_event(callback_func=callback, **kwargs)

    def show_infos(self, turn=0, phase='Player Turn', callback=None, **kwargs):
        obj = Turn(phase, turn, self.windowsize[0], self.windowsize[1])
        self.infolayer.add(obj)
        obj.do(FadeIn(0.5) + Delay(1) + FadeOut(0.5) + CallFunc(self._residual, obj=obj,
                callback=callback, **kwargs))

    def update_person(self, i=0, **kwargs):
        """
        this method will be called recursively until all people in person_list are updated
        after that, get turn event's to execute
        :param i: the number of person in person list to update
        :param kwargs: include reset now
        :return:
        """
        if i < self.person_num:
            p = self.person_list[i]
            p.state = 'unmoved'
            p.moved = False
            if p.pid in self.map.person_container.controller:
                if self.map.person_container.controller[p.pid]==self.map.controller:
                    log = self.map.refresh_person(p.pid)
            prop = p.update_hp(False)
            if prop != p.blood.prop:
                p.do(CallFunc(self.focus, p.pid) + Delay(0.2) + CallFunc(p.blood.set_angle, prop)
                     + CallFunc(self.update_person, i+1, **kwargs))
            else:
                self.update_person(i+1, **kwargs)
        else:
            self.get_next_event(**kwargs)

    def player_turn(self, **kwargs):
        """
        before player could give commands, execute other affairs
        consider if all members have moved in auto_end mode
        :param kwargs:
        :return:
        """
        self._clear_map()
        director.window.remove_handlers(self)
        flag = False
        for p in self.people.values():
            if p.state is 'unmoved' and p.controller is 0:
                flag = True
                break

        def player_turn():
            director.window.push_handlers(self)
            print('player_turn push_handlers')
            # before executed, handlers should be removed

        if not flag:
            print('all members are moved')
            if self.settings['endturn_automatically']:
                self.end_turn()
            else:
                player_turn()
        else:
            player_turn()

    def ai_turn(self, **kwargs):
        if 'Reinforce' in kwargs.keys() and len(kwargs['Reinforce']) > 0:
            events = kwargs['Reinforce']
            self._reinforce(events, callback=self.ai_turn2)
        else:
            self.ai_turn2()

    def ai_turn2(self):
        self.person_list = list(self.people.values())
        self.person_num = len(self.person_list)
        self.update_person()

    def _callbk(self, **kwargs):
        self.person_list = list(self.people.values())
        self.person_num = len(self.person_list)
        self.update_person(**kwargs)

    def player_phase(self, **kwargs):
        """
        at the very beginning of player phase
        if has reinforce, fisrt execute resinforce, then update all people's info
        :param kwargs: include reinforce and reset now
        :return:
        """
        if 'Reinforce' in kwargs.keys() and len(kwargs['Reinforce']) > 0:
            events = kwargs.pop('Reinforce')
            self._reinforce(events, callback=self._callbk, **kwargs)
        else:
            self.person_list = list(self.people.values())
            self.person_num = len(self.person_list)
            self.update_person(**kwargs)
        pass

    def ai_phase(self):
        obj = Turn('Ally Phase', self.map.turn, self.windowsize[0], self.windowsize[1])
        self.infolayer.add(obj)
        obj.do(FadeIn(0.5) + Delay(1) + FadeOut(0.5) + CallFunc(self._residual, obj=obj,
                                                                callback=self.ai_turn))
        pass

    def execute_turn_event(self, i=0, callback_func=None, **kwargs):

        if i < self.turn_length:
            event = self.turn_event[i]
            if (event['Side'] is None or self.map.controller == event['Side']) \
                and (event['Turn'] is None or self.map.turn == event['Turn']) \
                    and check_condition(event['Condition'], self.map):
                    if 'Reconstruct' in event.keys():
                        self.reconstruct(event['Reconstruct'])
                    print(event)
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
            print(callback_func, kwargs)
            callback_func.__call__(**kwargs)

    def _sequential_move(self, dst):
        # move person of pid through the trace dst
        # at start of this period, remove handlers to avoid events
        action = CallFunc(self.menulayer.disapper)
        for x,y in dst:
            action = action + MoveTo(coordinate(x, y, self.size),
                                     moving[self.settings['moving']])
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
        self.people[pid].set_moved()

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
                                      controller[pid])
            self.person_layer.add(self.people[pid])
            self.focus(pid)
            self.cells[position[pid]].person_on = pid
            actionlist.append((self.people[pid], CallFunc(self.focus, pid) + FadeIn(1.5)))
        self._repaint()
        print(callback, kwargs)
        actionlist.append((self, CallFunc(callback.__call__, **kwargs)))
        Sequencial(actionlist).excute()

    def _repaint(self):
        for cell in self.cells.values():
            if cell.state is 'default':
                cell.change_source(opacity=0)
            elif cell.state in ['in_self_moverange',    'in_enemy_moverange',    'in_ally_moverange', 'uncross_inrange']:
                cell.change_source('blue')
            elif cell.state in ['target', 'in_attackrange']:
                cell.change_source('red')
            elif cell.state in ['in_self_attackrange', 'execute_object', 'door', 'in_self_wandrange']:
                cell.change_source('green')
            else:
                pass
        for person in self.people.values(): #type:Charactor
            if person.state is 'selected':
                person.scale = 1.2
            else:
                person.scale = 1
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
            self.cursor.position = i*self.size, j*self.size

        if x >= self.windowsize[0] // 2:
            self.wpinfo.position = (0, 0)
        else:
            self.wpinfo.position = (self.windowsize[0] // 2, 0)

        #     self._repaint()
        #     cell = self.cells[(i, j)]
        #     cell.opacity = opacity[cell.state]
        # pass

    def on_key_press(self, symbol, modifiers):
        x, y = self.cursor.position
        i, j = x // self.size, y // self.size
        self.mouse_pos = i, j
        if symbol == key.UP and self._in_arena(i, j+1):
            self.cursor.position = i * self.size, (j + 1) * self.size
        elif symbol == key.DOWN and self._in_arena(i, j - 1):
            self.cursor.position = i * self.size, (j - 1) * self.size
        elif symbol == key.LEFT and self._in_arena(i - 1, j):
            self.cursor.position = (i - 1) * self.size, j * self.size
        elif symbol == key.RIGHT and self._in_arena(i + 1, j ):
            self.cursor.position = (i + 1)  * self.size, j * self.size
        elif symbol == key.ENTER:
            self.mouse_btn = mouse.LEFT
            self._state_control[self.state].__call__()
        elif symbol == key.BACKSPACE:
            self.mouse_btn = mouse.RIGHT
            self._state_control[self.state].__call__()


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
            self.item = None
        elif self.state in ['wand_type0','wand_type1','wand_type2','wand_type3',
                            'wand_type4', 'wand_type5', 'wand_type6', 'wand_type7_confirm',
                            'wand_type8', 'wand_type9']:
            self.wand(self.avl)
            self.item = None
        else:
            self.menu = Ordermenu(self)
            self.add_menu(self.menu)
        self.state = 'valid_dst'
        for pid in self._reset_person.keys():
            self.people[pid].state = self._reset_person[pid]
        for keys in self._reset_cell.keys():
            self.cells[keys].state = self._reset_cell[keys]
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

    def _set_areastate(self, area, state, repaint=True):
        for i, j in area:
            self.cells[(i, j)].state = state
        if repaint:
            self._repaint()

    def _set_moverange(self, pid, valid):
        _area = self.map.get_attack_range(pid, valid)
        self._set_areastate(_area[1], 'in_attackrange', False)
        self._set_areastate(_area[2], 'uncross_inrange', False)
        self._repaint()
        pass

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
        this is the most important part in interactions
        it defines a series of state so that different method will be called according to the state
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
            'show_rng': self._show_rng,
            'show_thumb': self._show_thumb,
        }

    def _callback(self, **kwargs):
        director.window.remove_handlers(self)
        director.window.push_handlers(self)
        print('callback push_handlers')
        self.state = 'default'

    def _default(self):
        """
        0   default
        not any army is selected
        event handler should be true to wait for commands
        consider end_turn menu only under this state
        :return:
        """

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
                    self.state = 'valid_select'
                    self._set_areastate(valid[pid], 'in_self_moverange', False)
                    self._set_moverange(pid, valid)
                else:
                    self.state = 'invalid_select'
                    _area = set(), set(), set()
                    if pid in invalid.keys():
                        tmp = self.map.move_and_attack_range(pid)
                        area = set(tmp[0])
                        self.people[pid].state = 'moved'
                        _area = set(), tmp[2], set()
                    elif pid in ally.keys():
                        area = ally[pid]
                        _area = self.map.get_attack_range(pid, ally)
                    elif pid in enemy.keys():
                        area = enemy[pid]
                        _area = self.map.get_attack_range(pid, enemy)
                    else:
                        area = set()
                        pass

                    self._set_areastate(_area[1], 'in_attackrange', False)
                    self._set_areastate(_area[2], 'uncross_inrange', False)
                    self._set_areastate(area, ctrl2map_moverange[self.map.person_container.controller[pid]], False)
                    self._repaint()
            else:
                self._clear_map()
                pass
        elif self.mouse_btn == 4:
            if self.cells[self.mouse_pos].person_on is not None:
                pid = self.cells[self.mouse_pos].person_on
                select = self.people[pid].person
                director.window.remove_handlers(self)
                self.info = Personinfo(select, callback=self._callback, map=self.map)
                self.infolayer.add(self.info)
                self.state = 'person_info'
                print(self.map.person_container.AItype[pid])
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
                pid = self.selected
                dst = self._mapstate[0][pid][self.target][1]

                self.state = 'valid_dst'
                self.cells[self.target].person_on = self.selected
                self.cells[self.origin_pos].person_on = None
                self.menu = Ordermenu(self)

                self.people[pid].do(self._sequential_move(dst) + CallFunc(self.add_menu, self.menu))
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
        # at present has nothing to do, all is handled by menu
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
                x, y = self.position
                self.hitrate.position = -x, -y
                self.hitrate.display([str(hitr)])
                self.state = 'wand_type1_confirm'
                self.allow_move = False
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

    def _show_rng(self):
        if self.mouse_btn == 4:
            self._clear_map()
        elif self.mouse_btn == 1:
            pass

    def _show_thumb(self):
        if self.mouse_btn == 4:
            self.infolayer.remove(self.thumb)
            del self.thumb
            self.state = 'default'
        elif self.mouse_btn == 1:
            pass

    def get_next_to_delete(self):
        try:
            pid = next(self.iter)
        except:
            self.get_next_event(reset=False)
            return
        person = self.people[pid].person
        if person.ability['HP'] <= 0:
            self.people[pid].do(FadeOut(2)+CallFunc(self._delete_person, pid))
        else:
            self.get_next_to_delete()
        pass

    def excute_event(self, i, reset=False):
        if i < self.general_length:
            event = self.general[i]
            if check_condition(event['Condition'], self.map):
                if 'Reconstruct' in event.keys():
                    self.reconstruct(event['Reconstruct'])
                self.eventdisplay(
                    event=event, map=self.map,
                    dialog_type=event['Text_type'], dialog_info=self.dialog_info,
                    w=self.windowsize[0], h=self.windowsize[1],
                    callback=self.get_next_event, i=i+1, reset=reset
                )
            else:
                self.get_next_event(i+1, reset=reset)
        else:
            if reset is True:
                self.focus('1')
            self.map.take_turn(self)
            pass

    def get_next_event(self, i=0, **kwargs):
        """
        the two method get_next_event and excute event are combined
        they are seperated for sake of reinforce
        :param i:
        :param kwargs:
        :return:
        """
        if 'Reinforce' in kwargs.keys() and len(kwargs['Reinforce']) > 0:
            events = kwargs.pop('Reinforce')
            self._reinforce(events, callback=self.excute_event, i=i, **kwargs)
        else:
            self.excute_event(i, **kwargs)


    def _battle(self, layer, **kwargs):
        director.window.remove_handlers(self)
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
                        self._reset_cell[(x, y)] = self.cells[(x, y)].state

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
            self._reset_cell[self.people[pid].pos] = self.cells[self.people[pid].pos].state
            self.cells[self.people[pid].pos].state = 'execute_object'

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
            action = CallFunc(self._set_moved, pid, dst) \
                 + CallFunc(self._clear_map) + CallFunc(self._push_scene, Battlescene, callback=self._clear)

        else:
            # from ai movements
            pid = kwargs['pid']
            dst = kwargs['dst']
            valid = kwargs['vld']
            self.battlelist = kwargs['battlelist']
            self._set_areastate(valid[pid], 'in_enemy_moverange', False)
            self._set_moverange(pid, valid)
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
        """

        """
        self._clear_map()
        self.map.controller = 1
        self.map.reset_state(0)
        director.window.remove_handlers(self)
        count, _ = self.map.count_army_population()
        if count[1] == 0:
            self.map.send_mapstate()
            self.map.controller = 2
            if count[2] == 0:
                self.map.send_mapstate()
                self.next_round()
            else:
                self.map.controller = 2
                obj = Turn('Ally Phase', self.map.turn, self.windowsize[0], self.windowsize[1])
                self.infolayer.add(obj)
                obj.do(FadeIn(0.5) + Delay(1) + FadeOut(0.5) + CallFunc(self._residual, obj=obj,
                                                                         callback=self.ai_turn))
        else:
            obj = Turn('Enemy Phase', self.map.turn, self.windowsize[0], self.windowsize[1])
            self.infolayer.add(obj)
            obj.do(FadeIn(0.5) + Delay(1) + FadeOut(0.5) + CallFunc(self._residual, obj=obj,
                                                                callback=self.ai_turn))

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
            action = CallFunc(self._set_moved, pid, dst) + \
                     CallFunc(self._clear_map) + Delay(0.5) + CallFunc(self.get_next_to_delete)
        else:
            pid = kwargs['pid']
            dst = kwargs['dst']
            valid = kwargs['vld']
            self._set_areastate(valid[pid], 'in_enemy_moverange', False)
            self._set_moverange(pid, valid)
            action = self._sequential_move(dst) + CallFunc(self._set_moved, pid, dst) + \
                     CallFunc(self._clear_map) + Delay(0.5) + CallFunc(self.get_next_to_delete)
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
        self.state = 'valid_select'
        self.menulayer.disapper()
        self.cells[self.target].person_on = None
        self.cells[self.origin_pos].person_on = self.selected
        self.people[self.selected].position = coordinate(self.origin_pos[0], self.origin_pos[1], self.size)
        self.target = None

    def save(self):
        # director.window.push_handlers(self)
        self.menulayer.disapper()
        self.state = 'default'
        # self.map.map_save()
        sl = Saveload(self.windowsize[0], self.windowsize[1], self)
        self.add(sl)
        sl.position = -self.position[0], -self.position[1]

    def load(self):
        self.menulayer.disapper()
        self.state = 'default'
        sl = Saveload(self.windowsize[0], self.windowsize[1], self, 'load')
        self.add(sl)
        sl.position = -self.position[0], -self.position[1]

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
        self._set_areastate([self.target], 'target', False)
        self.state = 'choose_exchange'
        for pid in exc:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_exchange'
            self._reset_cell[self.people[pid].pos] = self.cells[self.people[pid].pos].state
            self.cells[self.people[pid].pos].state = 'execute_object'

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
            self._reset_cell[self.people[pid].pos] = self.cells[self.people[pid].pos].state
            self.cells[self.people[pid].pos].state = 'execute_object'

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
            self._reset_cell[self.people[pid].pos] = self.cells[self.people[pid].pos].state
            self.cells[self.people[pid].pos].state = 'execute_object'

        self.talk_dict = talk_dict
        self._repaint()

    def eventdisplay(self, callback=None, **kwargs):
        display = Eventdisplay(callback=callback, **kwargs)
        self.add(display)
        display.display()

    def reconstruct(self, rec, ty='default'):
        if rec is not None:
            if ty is 'default':
                self.map.reconstruct_log.append(rec)
            if type(rec) is str:
                path = self.map.global_vars.data.get_root("data")
                _rec = json.load(open(path + rec, "r"))
            else:
                _rec = rec
            self.map.map_reconstruct(_rec)
            x, y, m, n = _rec["Anchor_X"], _rec["Anchor_Y"], _rec["M"], _rec["N"]
            width, height = m * self.size, n * self.size
            _x, _y = (x * 2 + m - 1) / 2, (y * 2 + n - 1) / 2
            recon = Sprite(_rec['Pic'], position=coordinate(_x, _y, self.size))
            recon.scale_x, recon.scale_y = width / recon.width, height / recon.height
            self.remove(self.cell_layer)
            self.remove(self.person_layer)
            self.add(recon)
            self.add(self.person_layer)
            self.add(self.cell_layer)
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

    def before(self):
        event = self.map.pre
        before = Afterevent(event=event, map=self.map,
                    dialog_type='S', dialog_info=self.dialog_info,
                    w=self.windowsize[0], h=self.windowsize[1],
                    callback=self._before_callback)
        self.add(before)
        x, y = self.position
        before.position = -x, -y
        self.do(Delay(0.5) + CallFunc(before.display))

    def _before_callback(self):
        director.push(Scene(self, self.menulayer, self.infolayer))

        self.next_round()

    def jump(self):
        self.menulayer.disapper()
        director.window.push_handlers(self)
        self.map.global_vars.flags['VIC_FLAG00001'] = True
        self.state = 'default'

    def showattrng(self):
        self.menulayer.disapper()
        area = self.map.collective_range()
        self._set_areastate(area, 'in_attackrange')
        self.state = 'show_rng'
        director.window.push_handlers(self)
        pass

    def showthumb(self):
        self.menulayer.disapper()
        self.state = 'show_thumb'
        director.window.push_handlers(self)
        minimap = self.map.get_thumbnail()
        self.thumb = Thumb(minimap, self.w, self.h)
        self.infolayer.add(self.thumb)
        self.thumb.position = (self.windowsize[0] - 10*self.w)//2 , \
                              (self.windowsize[1] - 10*self.h)//2

    def status(self):
        self.menulayer.disapper()
        self.state = 'person_info'
        self.info = Info()
        content = []
        content.append(self.map.vic)
        content.append('Turn %d'%self.map.turn)
        count = self.map.count_army_population()[1] #type:List[Dict]
        for dic in count:
            for name in dic:
                num = dic[name]
                content.append(name + ': %d'%num)

        self.info.display(content, font_color=(0,0,0,255), back=True)
        print(content)
        self.infolayer.add(self.info)
        director.window.push_handlers(self)


    def setting(self):
        self.menulayer.disapper()
        director.window.push_handlers(self)
        print(self.settings)
        self.state = 'default'

    def _next(self, **kwargs):
        map, metadata = self.map.global_vars.new_map(kwargs['Map']) #type: map_controller.Main, dict
        title = map.title
        obj = Chapter(title, w=self.windowsize[0], h=self.windowsize[1])
        print(self.windowsize)
        self.infolayer.add(obj)
        obj.do(FadeIn(0.5) + Delay(1) + CallFunc(self._residual2, map, metadata))

    def _residual2(self, map, metadata):

        if 'Preparation' in metadata.keys():
            print(metadata['Preparation'])
        menulayer = Menulayer()
        infolayer = Layer()
        arena = Arena(map, menulayer, infolayer, self.size)
        arena.visible = False

        class Transition(FadeTransition):
            def finish(self):
                super().finish()
                arena.before()

        director.run(Transition(Scene(arena, menulayer, infolayer)))

    def remove(self, obj):
        super().remove(obj)
        del obj

    def coordinate_t(self, x, y):
        pos = self._coordinate(x, y)
        i = int(pos[0] // self.size)
        j = int(pos[1] // self.size)
        return i, j

    def update(self, dt,d=0):
        if self.allow_move:
            x1, y1 = self._update
            x0, y0 = self.position
            if x0 > d and x1 > 0 or x0 < -(self.width - self.windowsize[0]) - d and x1 < 0:
                x1 = 0
            if y0 > d and y1 > 0 or y0 < -(self.height - self.windowsize[1]) - d and y1 < 0:
                y1 = 0
            self.position = self.position[0] + x1, \
                            self.position[1] + y1
            if hasattr(self, 'thumb'):
                self.thumb.update(x0, y0)

    def _coordinate(self,x, y):
        return ((x - self.anchor_x - self.position[0]) // self.scale + self.anchor_x) ,\
              ((y - self.anchor_y - self.position[1]) // self.scale + self.anchor_y)

class Board():
    def __init__(self, w=800, h=600, margin=20, step=-5):
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
                return (self.step,  self.step)
            elif y < self.margin:
                return (self.step, -self.step)
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

    layer = Layer()
    event = map.pre
    before = Afterevent(event=event, map=arena.map,
                        dialog_type='S', dialog_info=arena.dialog_info,
                        w=arena.windowsize[0], h=arena.windowsize[1],
                        callback=arena._before_callback)

    layer.add(before)

    class Transition(FadeTransition):
        def finish(self):
            super().finish()
            before.display()


    scene = Transition(Scene(layer), duration=1.5)
    director.push(scene)
    print(director.scene_stack)

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
    pyglet.resource.path = ['../img']
    pyglet.resource.reindex()
    director.init(caption='3X-Project', width=1280, height=720)
    menulayer = Menulayer()
    infolayer = Layer()
    arena = Arena(map_init(), menulayer, infolayer, size=80)
    director.run(Scene(arena, menulayer, infolayer))
    arena.next_round()
    pyglet.image._codecs





