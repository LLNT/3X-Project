# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:02
'''
import pyglet

from cocos.layer import Layer, ColorLayer, ScrollableLayer
from cocos.director import director
from cocos.scene import Scene
from cocos.actions import CallFunc, MoveTo, Delay, FadeOut
from cocos.scenes import FadeTransition
from display_item.sprite import Charactor, Cell
from display_item.state2color import *
from display_item.info import Personinfo, Battleinfo, Info
from display_item.menu import Ordermenu, Weaponmenu, Endturn, Menulayer, Showweapon, Showwand, Weaponexchange, Listwand
from display_item.background import Background
from display_item.battle_scene import Battlescene, Wandtype0, Wandtype1, Wandtype2, Wandtype3
from display_item.ring import PerSpr
from display_item.getitem import Getitem

import map_controller
from global_vars import Main as Global
from data_loader import Main as Data
from person_container import Main as Person_Container
from terrain_container import Main as Terrain_Container
from wand import Type1, Type3



class Arena(ScrollableLayer):
    # the holder of map and roles
    is_event_handler = True

    def __init__(self, map, w, h, menulayer,size=80):
        super(Arena, self).__init__()

        # initialize the holder according to the map
        self.width, self.height = w*size, h*size
        self.windowsize = director.get_window_size()
        self.anchor = self.width // 2, self.height // 2
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
            self.people[pid] = PerSpr(person, 1, size, position[pid], controller[pid], bk_color=(220,220,220))
            self.add(self.people[pid])
            self.cells[position[pid]].person_on = pid

        self.menulayer = menulayer


        self.board = Board(self.width, self.height)
        self._update = (0, 0)
        # self.schedule(self.update)

        self.anchor = self.width//2, self.height//2

        self._clear_map()


        self.next_round()

        window = director.window



    def on_return(self, person, getitem=None):
        if getitem is not None:
            self.add(Getitem(person,getitem,self.map.global_vars.flags['Have Transporter'],self.map))
            self.is_event_handler = False
        else:
            self.get_next_to_delete()
            self.map.take_turn(self)
            for person in self.people.values():
                person.update_hp()

    def end_getitem(self):
        director.window.push_handlers(self)
        self.get_next_to_delete()
        self.map.take_turn(self)
        for person in self.people.values():
            person.update_hp()
        self.state = 'default'
        print(self.is_event_handler)

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
        if self.is_event_handler:
            pos = self._coordinate(x, y)
            self._update = self.board.get_dir(pos[0], pos[1])
            i, j = self.coordinate_t(x, y)
            if self._in_arena(i, j):
                self._repaint()
                cell = self.cells[(i, j)]
                cell.color = mapstate2color_motion[cell.state]
                cell.opacity = opacity[cell.state]
            pass


    def on_mouse_press(self, x, y, buttons, modifiers):
        # according to the state link to correct function
        if self.is_event_handler:
            print(self.state)
            self.mouse_pos = self.coordinate_t(x, y)
            self.mouse_btn = buttons
            self._state_control[self.state].__call__()
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        # if scroll_y == 1.0:
        #     self.scale = self.scale * 1.1
        # else:
        #     self.scale = self.scale * 0.9
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == 1 and self.state is 'default':
            self.position = self.position[0] + dx, self.position[1] + dy

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

            self.item = None
        elif self.state is 'choose_support' or self.state is 'choose_exchange':
            if self.state is 'choose_support':
                for pid in self.sup_dict:
                    self.people[pid].state = self._reset_person[pid]
            else:
                for pid in self.exc:
                    self.people[pid].state = self._reset_person[pid]
            self.menu = Ordermenu(self)
            self._add_menu(self.menu)
            self.is_event_handler = False

        elif self.state in ['wand_type0','wand_type1','wand_type2','wand_type3']:
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

    def _seq_add(self, item):
        self.menulayer.add(item)

    def _set_state(self, state):
        self.state = state

    def _add_menu(self, menu, dt=0.1):
        self.menulayer.appear()
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
        self.menulayer.disapper()
        self.iter = iter(self.people)
        self.item_w = None
        self.avl = None
        self.excpid = None
        self.allow_cancel = True
        self.wandlist_type0 = self.wandlist_type1 = self.wandlist_type2 = []
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
            person.update_hp()

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
            'choose_support': self._choose_support, 8: self._choose_support,
            'end_turn': self._end_turn, 9: self._end_turn,
            'wand_type0': self._wand_type0,10:self._wand_type0,
            'wand_type1': self._wand_type1,
            'wand_type1_confirm': self._wand_type1_confirm,
            'wand_type2': self._wand_type2,
            'wand_type3': self._wand_type3,
            'wand_type3_confirm': self._wand_type3_confirm,
            'choose_exchange': self._choose_exchange
        }

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
            else:
                self.end = Endturn(self)
                self.menulayer.add(self.end)
                self.menulayer.appear()
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
            if not self._in_arena(self.mouse_pos[0], self.mouse_pos[1]):
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
            self.attacking()
            pass

    def _push_scene(self, layer):
        scene = Scene((layer(self, self.windowsize[0], self.windowsize[1])))
        director.push(FadeTransition(scene, duration=1.5))

    def _show_battle_result(self):
        # 7   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5

        self.is_event_handler = False
        self.get_next_to_delete()

    def _choose_support(self):
        # 8   show_battle_result
        # showing battle result, push to another scene
        # if confirm, push battle scene and then return to 1, else turn to 5
        if self.mouse_btn is 1:
            if self.mouse_pos in self.sup_dict.values():
                self.map.build_support(self.selected, self.cells[self.mouse_pos].person_on)
                for pid in self.sup_dict:
                    self.people[pid].state = self._reset_person[pid]
                self.move()
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
                pid = self.selected
                dst = self._mapstate[0][self.selected][self.target][1]
                self.is_event_handler = False
                action = self._sequential_move(pid, dst)
                obj = self.people[pid]
                obj.do(action + CallFunc(self._push_scene, Wandtype0) +
                       CallFunc(self._clear_map) + CallFunc(self._set_state, 'show_battle_result'))
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
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
            self.is_event_handler = False
            action = self._sequential_move(pid, dst)
            obj = self.people[pid]
            obj.do(action + CallFunc(self._push_scene, Wandtype1) +
                   CallFunc(self._clear_map) + CallFunc(self._set_state, 'show_battle_result'))
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
                self.menulayer.add(Listwand(target.item, self, type=2))
                self.is_event_handler = False
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
                self._add_menu(Listwand(target.item, self, type=3))
                self.is_event_handler = False
            else:
                self._reset()
            pass
        pass

    def _wand_type3_confirm(self):
        self.remove(self.hitrate)
        if self.mouse_btn is 1:
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
            self.is_event_handler = False
            action = self._sequential_move(pid, dst)
            obj = self.people[pid]
            obj.do(action + CallFunc(self._push_scene, Wandtype3) +
                   CallFunc(self._clear_map) + CallFunc(self._set_state, 'show_battle_result'))
        else:
            self.wandlist_type3.pop()
            self.state = 'wand_type3'
            self._add_menu(Listwand(self.wandlist_type3[2].item, self, type=3))
            pass
        pass

    def _choose_exchange(self):
        if self.mouse_btn == 4:
            self._reset()
            pass
        elif self.mouse_btn == 1:
            pid = self.cells[self.mouse_pos].person_on
            if pid is not None and pid in self.exc:
                self.menulayer.add(Weaponexchange(self.people[self.selected].person.item, self,
                                                  (-self.windowsize[0], 0)), name='left')
                self.menulayer.add(Weaponexchange(self.people[pid].person.item, self,
                                                  (-self.windowsize[0]//2, 0)), name='right')
                self.is_event_handler = False
                self.excpid = pid
            pass

    def get_next_to_delete(self):
        try:
            pid = next(self.iter)
        except:
            self._clear_map()
            return
        person = self.people[pid].person
        if person.ability['HP'] <= 0:
            self.people[pid].do(FadeOut(2)+CallFunc(self._delete_person, pid))
        else:
            self.get_next_to_delete()
        pass

    def _delete_person(self, pid):
        person = self.people[pid]
        self.people.pop(pid)
        self.remove(person)
        del person
        self.get_next_to_delete()



    def _simplefied_battle(self):
        self.is_event_handler = False
        self.add(BattleSim())
        self._set_state('show_battle_result')
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

    def wanduse(self, item_w):
        self.menulayer.disapper()
        area = []
        max_range = item_w.itemtype.max_range
        min_range = item_w.itemtype.min_range
        if max_range == -1:
            person = self.people[self.selected].person
            max_range = max(1, person.ability['MGC'])
        (i, j) = self.target
        for distance in range(min_range, max_range + 1):
            for dx in range(distance + 1):
                dy = distance - dx
                for x, y in [(i + dx, j + dy), (i + dx, j - dy), (i - dx, j + dy), (i - dx, j - dy)]:
                    if x in range(self.w) and y in range(self.h):
                        area.append((x, y))
        self._set_areastate(area, 'in_self_wandrange')
        self.item_w = item_w
        self.is_event_handler = True
        if item_w.itemtype.wand['Type'] == 0:
            self.state = 'wand_type0'
        elif item_w.itemtype.wand['Type'] == 1:
            self.state = 'wand_type1'
        elif item_w.itemtype.wand['Type'] == 2:
            self.state = 'wand_type2'
        elif item_w.itemtype.wand['Type'] == 3:
            self.state = 'wand_type3'
        else:
            self._add_menu(Showwand(self.avl, self))

    def attacking(self, **kwargs):
        if len(kwargs) is 0:
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
        else:
            pid = kwargs['pid']
            dst = kwargs['dst']
            rng = kwargs['rng']
            self.battlelist = kwargs['battlelist']
            self._set_areastate(rng, 'in_enemy_moverange')
        self.is_event_handler = False
        action = self._sequential_move(pid, dst)
        obj = self.people[pid]
        obj.do(action + CallFunc(self._push_scene, Battlescene) +
               CallFunc(self._clear_map) + CallFunc(self._set_state, 'show_battle_result'))

    def attack(self):
        self.is_event_handler = False
        self._set_areastate([self.target], 'target')
        items = self.people[self.selected].person.item
        self._add_menu(Weaponmenu(items, self.map, self))
        pass

    def item_show(self):
        self.is_event_handler = False
        self._set_areastate([self.target], 'target')
        items = self.people[self.selected].person.item
        self._add_menu(Showweapon(items, self))
        pass

    def end_turn(self):
        self._clear_map()
        self.map.controller = 1
        self.map.reset_state(0)
        self.is_event_handler = False
        self.map.ai_turn2(self)

    def move(self, **kwargs):
        self.is_event_handler = False
        if len(kwargs) is 0:
            pid = self.selected
            dst = self._mapstate[0][self.selected][self.target][1]
        else:
            pid = kwargs['pid']
            dst = kwargs['dst']
            rng = kwargs['rng']
            self._set_areastate(rng, 'in_enemy_moverange')
        action = self._sequential_move(pid, dst)
        obj = self.people[pid]
        obj.do(action + CallFunc(self._clear_map) + CallFunc(self.map.take_turn, self))
        pass

    def wand(self, avl):
        self.is_event_handler = False
        self._set_areastate([self.target], 'target')
        self._add_menu(Showwand(avl, self))
        self.avl = avl

    def cancel(self):
        self.is_event_handler = True
        self._set_areastate([self.target], 'in_self_moverange')
        self.state = 'valid_select'
        self.menulayer.disapper()
        self.target = None
        pass

    def use(self, item):
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        person = self.people[pid].person
        obj = self.people[pid]
        action = self._sequential_move(pid, dst)
        obj.do(action + CallFunc(person.use_item, item) + CallFunc(self._clear_map)
               + CallFunc(self.map.take_turn, self))
        pass

    def equip(self, item):
        pid = self.selected
        person = self.people[pid].person
        person.equip(item)
        self.item_show()

    def banish(self, item):
        pid = self.selected
        person = self.people[pid].person
        person.call_banish(item)
        self.item_show()

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
        self._set_areastate([self.target], 'target')
        self.state = 'choose_exchange'
        for pid in exc:
            self._reset_person[pid] = self.people[pid].state
            self.people[pid].state = 'can_exchange'
        self.exc = exc
        self._repaint()
        self.menulayer.disapper()
        self.is_event_handler = True

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
        self.is_event_handler = False
        self.allow_cancel = False

    def wandrpr(self, item):
        self.wandlist_type2.append(item)
        pid = self.selected
        dst = self._mapstate[0][self.selected][self.target][1]
        self.is_event_handler = False
        action = self._sequential_move(pid, dst)
        obj = self.people[pid]
        obj.do(action + CallFunc(self._push_scene, Wandtype2) +
               CallFunc(self._clear_map) + CallFunc(self._set_state, 'show_battle_result'))

    def wandstl(self, item):
        self.wandlist_type3.append(item)
        self.is_event_handler = True
        self.state = 'wand_type3_confirm'
        user, wand, target, self.map, self.target, _ = self.wandlist_type3
        hitr_3 = Type3(user, wand, target, self.map, self.target, item).simulate()
        self.hitrate = Info()
        self.add(self.hitrate)
        self.hitrate.display([str(hitr_3)])



    def remove(self, obj):
        super().remove(obj)
        del obj

    def coordinate_t(self, x, y):
        pos = self._coordinate(x, y)
        i = int(pos[0] // self.size)
        j = int(pos[1] // self.size)
        return i, j

    def update(self, dt):
        self.position = self.position[0] + self._update[0], \
                        self.position[1] + self._update[1]

    def _coordinate(self,x, y):
        return ((x - self.anchor_x - self.position[0]) // self.scale + self.anchor_x) ,\
              ((y - self.anchor_y - self.position[1]) // self.scale + self.anchor_y)

class Board():
    def __init__(self, w=800, h=600, margin=20, step=2):
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
                return (self.step, self.step)
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
    map, w, h = map_init()
    size = 80
    director.init(caption='3X-Project', width=1280, height=720)


    menulayer = Menulayer()
    director.run(Scene(Arena(map, w, h, menulayer, size), menulayer))





