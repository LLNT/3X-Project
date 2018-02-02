import cocos
import pyglet
from cocos.actions import MoveTo, Delay, CallFunc
from cocos.director import director
from cocos.scene import Scene
from cocos.scenes import ShuffleTransition
from cocos.sprite import Sprite

import map_controller
from audio import Audiolayer
from data_loader import Main as Data
from display_item.battle_scene import Battlescene
from display_item.menu import Optionmenu, Weaponselect
from display_item.info import Personinfo, Battleinfo
from display_item.loading import Loading

from battle import Battle
from global_vars import Main as Global
from person import Person
from person_container import Main as Person_Container
from terrain_container import Main as Terrain_Container
from utility import *
import time

class Arena(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):

        pyglet.resource.path = ['../img']
        pyglet.resource.reindex()
        self.size = 80
        self.select = None #当前选中的角色
        self.state = 'none' # 0：默认 什么都没选中； 1：选中一个友军 左击移动右击取消 2：选中一个敌军 任何操作都取消 3： 正在显示某个人的信息 任何操作返回
        data = Data()
        global_vars = Global(data)
        terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
        person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
        map1 = map_controller.Main(terrain_container_test, person_container_test, global_vars)
        self.w = terrain_container_test.M
        self.h = terrain_container_test.N

        super(Arena, self).__init__(r=0,g=0,b=0,a=255,width=self.w*self.size,height=self.h*self.size)

        self.tiles = []
        for x in range(self.w):
            tl_x = []
            for y in range(self.h):
                tile = MapCell(pos=coordinate(x, y, self.size), size=self.size)
                self.add(tile)
                tl_x.append(tile)
            self.tiles.append(tl_x)

        self.map = map1
        position = map1.person_container.position
        controller = map1.person_container.controller
        people = map1.person_container.people
        self.person = {}
        self.map2per = {}
        for p in people:
            id = p.pid
            (x, y) = position[id]
            if controller[id] == 1:
                state = 'enemy'
            else:
                state = 'self'
            self.map2per[(x, y)] = p
            self.person[id] = MapPer(person=p, pos=coordinate(x, y, self.size), size=self.size, state=state)
            self.add(self.person[id])

        self.text = cocos.text.RichLabel('ROUND 1' ,
                                     font_name='times new roman',
                                     font_size=36,
                                     position=(0, 420),
                                    color = (127, 255, 170, 255))
        self.add(self.text)
        self.end_turn = Sprite(image='ring.png', position=(560,200), color=MAROON, scale=0.8)

        self.add(self.end_turn)
        self.add(cocos.text.RichLabel(text='END', position=(520, 190), font_size=30))
        self.mapstate = self.map.send_mapstate()

        self.highlight = set()
        self.mouse_select = None
        self.target = None
        self.item = None
        self.origin_color = None
        self.mark = set()
        self.add(Audiolayer())

        self.next_round()


    def move(self, person, dst):
        obj = self.person[person.pid]
        action = self._sequential_move(person, dst)
        obj.do(action + CallFunc(self.clear_map) + CallFunc(self.take_turn))

    def _sequential_move(self, person, dst): #传入人物对象和移动轨迹
        map = self.map
        i, j = dst[-1]
        id = person.pid
        map.person_container.position[id] = i, j
        map.person_container.movable[id] = False
        self.mapstate = self.map.send_mapstate()
        if map.person_container.controller[id] == 0:
            self.person[id].state = 'moved'
        self.is_event_handler = False
        self.map2per[dst[-1]] = person
        action = Delay(0.1)
        for x,y in dst:
            action = action + MoveTo(coordinate(x, y, self.size), 0.5)
        return action

    def select_attack(self, person, dst, item):
        area = []
        max_range = item.itemtype.max_range
        min_range = item.itemtype.min_range
        i, j = dst[-1]
        for distance in range(min_range, max_range+1):
            for dx in range(distance+1):
                dy = distance - dx
                for x, y in [(i+dx, j+dy),(i+dx, j-dy),(i-dx, j+dy),(i-dx, j-dy)]:
                    if x in range(self.w) and y in range(self.h):
                        area.append((x, y))

        self.set_mapstate(area, 'in_self_attackrange')
        self.set_mapstate([self.target], 'target')
        self.state = 'wait_attack'
        self.dst = dst
        self._repaint()
        self.item = item

    def attack(self, battle_element):
        at, df, wp, map, pos = battle_element
        battle = Battle(at, df, wp, df.item[0], map, pos)
        res = battle.battle()
        del battle
        obj = self.person[at.pid]
        action = self._sequential_move(self.select, self.dst)
        obj.do(action + CallFunc(self._battle_scene, res) + CallFunc(self.clear_map)
               + CallFunc(self.take_turn))

    def _battle_scene(self, res):
        director.push(ShuffleTransition(Scene(Battlescene(res)), duration=1.5))

    def take_turn(self): #according to the controller, take turn of next charactor
        map = self.map
        if map.controller == 0:
            map.player_turn(self)
        else:
            map.ai_turn(self)

    def return_to_notdecide(self):
        select = self.select
        self.clear_map()
        self.select = select
        self.person[self.select.pid].state = 'selected'
        area = self.mapstate[0][select.pid]
        self.set_mapstate(area, 'in_self_moverange')
        self.set_mapstate([self.target], 'target')
        self.info.info_clear()
        self.menu = Weaponselect(self.select, self.dst)
        self.add(self.menu)

    def choose_new_target(self):
        self.set_mapstate([self.target], 'in_self_moverange')
        self.target = None
        self._repaint()
        self.state = 'valid_select'

    def next_round(self):
        self.map.turn += 1
        self.text.element.text = 'ROUND '+str(self.map.turn)
        self.map.controller = 0
        self.mapstate = self.map.send_mapstate()
        for p in self.person:
            if self.map.person_container.controller[p] == 1:
                self.person[p].state = 'enemy'
            else:
                self.person[p].state = 'self'
        self._repaint()
        if self.map.turn > 6 :
            director.pop()
        else:
            self.take_turn()

    def _repaint(self):
        for i in range(self.w):
            for j in range(self.h):
                self.tiles[i][j].color = map_state2color[self.tiles[i][j].state]
        for p in self.person:
            self.person[p].color = per_state2color[self.person[p].state]
        pass

    def on_mouse_motion(self, x, y, buttons, modifiers):
        if self.state == 'menu_display' or self.state == 'battle_info':
            return
        i, j = coordinate_t(x, y, self.size)
        if (x-560)**2 + (y-200)**2 < 80**2:
            self.end_turn.color = GOLD
        else:
            self.end_turn.color = MAROON

        if i in range(0, self.w) and j in range(0, self.h):
            self._repaint()
            cell = self.tiles[i][j]
            cell.color = map_state2color_motion[cell.state]
        else:
            pass
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.is_event_handler:
            i, j = coordinate_t(x, y, self.size)
            map = self.map
            valid, invalid, ally, enemy = self.mapstate
            if self.state == 'info': #显示信息界面 任何操作都返回
                self.info.info_clear()
                self.clear_map()
            elif self.state == 'invalid_select' or self.state == 'enemy_select' \
                    or self.state == 'ally_select': #选中一个敌军或友军 任何操作都返回
                self.clear_map()
            elif self.state == 'wait_attack': #等待下一步指令中，选中一个有效对象则进行战斗
                if buttons == 4:
                    self.return_to_notdecide()
                elif buttons == 1:
                    if (i, j) in self.map2per.keys(): #选中的是人
                        pid = self.map2per[(i, j)].pid
                        if self.tiles[i][j].state is 'in_self_attackrange' \
                                and self.map.person_container.controller[pid] == 1:

                            self.info.info_clear()
                            self.info = Battleinfo(self.select, self.map2per[(i, j)], self.item, self.map, self.target)
                            self.add(self.info)
                            self.state = 'battle_info'
                        else:
                            print('cannot attack')
                            self.return_to_notdecide()
                    else:
                        if self.tiles[i][j].state is 'in_self_attackrange':
                            print('not a person')

                        else:
                            print('not valid')
                        self.return_to_notdecide()
                        pass


                    pass

            elif self.state == 'battle_info':
                if buttons == 1:
                    print("attaking")
                    # self.move(self.select, self.dst)

                    self.attack(self.info.battle_element)
                    self.info.info_clear()
                elif buttons == 4:
                    self.return_to_notdecide()
            else: #其他情况 进行判断左击或右击
                if buttons == 1:
                    if self.end_turn.color == list(GOLD): #判断是否结束回合
                        map.controller = 1
                        map.reset_state(0)
                        self.is_event_handler = False
                        self.clear_map()
                        self.take_turn()
                        return
                    if self.state == 'none': #谁都没被选中，判断点击位置是否是人，标准状态
                        # 现在只有一个人
                        if (i, j) in self.map2per.keys(): #选中的是玩家角色
                            select = self.map2per[(i, j)] # type:Person
                            pid = select.pid
                            area, state = None, None
                            if pid in valid.keys(): #选中的是可移动角色
                                # 显示移动范围
                                self.select = select
                                self.state = 'valid_select'
                                state = 'in_self_moverange'
                                area = valid[pid]
                                self.person[pid].state = 'selected'

                            elif pid in invalid.keys(): #选中的是已行动的本方角色
                                self.state = 'invalid_select'

                            elif pid in enemy.keys():
                                self.state = 'enemy_select'
                                state = 'in_enemy_moverange'
                                area = enemy[pid]
                            elif pid in ally.keys():
                                self.state = 'ally_select'
                            else:
                                # 已经移动或其他原因
                                pass
                            if area is None or state is None:
                                return
                            self.set_mapstate(area, state)
                        else:
                            # 显示其他信息，不处理
                            return

                    elif self.state == 'valid_select':  # 已经选中一个可移动的人
                        id = self.select.pid
                        cell = self.tiles[i][j]
                        if cell.state is 'in_self_moverange':
                            self.target = (i, j)
                            self.set_mapstate([self.target], 'target')
                            dst = valid[id][(i, j)][1]
                            self.state = 'menu_display'
                            self.menu = Optionmenu(self.select, dst)
                            self.add(self.menu)
                            '''
                            # self.move(self.select, i, j)
                            self.sequential_move(self.select, dst)
                            # 显示移动确定选项
                            
                            
                            self.sequential_move(self.select, dst)
                            '''
                        else:
                            self.clear_map()

                elif  buttons == 4: #右击
                    if self.state == 'valid_select': # 已经选中一个人，改操作为取消
                        self.clear_map()
                    elif self.state == 'none': # 谁都没选中 显示选中者的信息
                        if (i, j) in self.map2per.keys(): #选中的是玩家角色
                            select = self.map2per[(i, j)] # type:Person
                            self.state = 'info' # 选中信息的界面状态
                            self.info = Personinfo(select)
                            self.add(self.info)

                        else:
                            pass # 显示地图信息？
                    else:
                        pass
                    pass
            '''
            

            if self.end_turn.color == list(GOLD):
                map.controller = 1
                map.reset_state(0)
                self.is_event_handler = False
                self.next_round()
            else:
                if i in range(0, self.w) and j in range(0, self.h):
                    if map.person_container.movable['1']:
                        map.person_container.position['1'] = i, j
                        map.person_container.movable['1'] = False
                        self.move('1', i, j)

            '''

    def set_mapstate(self, area, state):
        for i, j in area:
            self.tiles[i][j].state = state
        self._repaint()


    def _exit(self, scene):
        director.push(scene)

    def clear_map(self):
        self.state = 'none'
        for i in range(self.w):
            for j in range(self.h):
                self.tiles[i][j].state = 'none'
        if self.select is not None and self.person[self.select.pid].state is 'selected':
            self.person[self.select.pid].state = 'self'
            self.select = None

        self._repaint()


class MapCell(Sprite):
    def __init__(self, size=50,pos=None,state='none'):
        path = 'ring.png'
        super(MapCell, self).__init__(image=path)
        self.scale = size/self.height
        self.color = (255, 255, 255)
        self.position = pos
        self.state = state

class MapPer(Sprite):
    def __init__(self, person, size=50,pos=None, color=(135, 206, 235),state='none'):
        path = 'ring.png'
        super(MapPer, self).__init__(image=path)
        self.person = person
        self.scale = size/self.height * 0.8
        self.color = color
        self.position = pos
        self.state = state


if __name__ == '__main__':
    director.init(caption='3X-Project')
    director.run(Scene(Arena()))
