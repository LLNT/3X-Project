import cocos
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import MoveTo, Delay, sequence
from global_vars import Main as Global
from data_loader import Main as Data
from terrain_container import Main as Terrain_Container
from person_container import Main as Person_Container
import map_controller
from utility import *
class Arena(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        self.size = 80
        self.select = (0, 0)
        self.origin_color = WHITE
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
                tile = Tile(pos=coordinate(x, y, self.size), size=self.size)
                self.add(tile)
                tl_x.append(tile)
            self.tiles.append(tl_x)
        self.repaint(map1)
        self.map = map1

    def move(self, id, i, j):
        obj = self.person[id]
        print(obj)
        mov = MoveTo(coordinate(i, j, self.size), 2)
        obj.do(Delay(0.5)+ mov + cocos.actions.CallFunc(self.take_turn))


    def take_turn(self): #according to the controller, take turn of next charactor
        map = self.map
        if map.controller == 1:
            map.player_turn(self)
        else:
            map.ai_turn(self)

    def next_round(self):
        self.map.turn += 1
        if self.map.turn > 6 :
            director.pop()
        else:
            self.take_turn()



    def repaint(self, map_controller):
        position = map_controller.person_container.position
        controller = map_controller.person_container.controller
        self.person = {}
        for id in position:
            (x, y) = position[id]
            if controller[id] == 1 :
                color = ORANGE
            else:
                color = SKY_BLUE
            self.person[id] = Ally(pos=coordinate(x, y, self.size), color=color, size=self.size)
            self.add(self.person[id])


    def on_mouse_motion(self, x, y, buttons, modifiers):
        i, j = coordinate_t(x, y, self.size)
        if i in range(0, self.w) and j in range(0, self.h):
            i0, j0 = self.select
            self.tiles[i0][j0].color = self.origin_color
            self.origin_color = self.tiles[i][j].color
            self.tiles[i][j].color = LIGHT_PINK
            self.select = i, j

    def on_mouse_press(self, x, y, buttons, modifiers):
        i, j = coordinate_t(x, y, self.size)
        map = self.map
        map.controller = 0
        if i in range(0, self.w) and j in range(0, self.h):
            map.person_container.position['2'] = i, j
            map.person_container.movable['2'] = False

            self.move('2', i, j)
        else:
            self.next_round()





class Tile(Sprite):
    def __init__(self, size=50,pos=None):
        super(Tile, self).__init__(image='img/circle.png')
        self.scale = size/self.height
        self.color = (255, 255, 255)
        self.position = pos



class Ally(Sprite):
    def __init__(self, size=50,pos=None, color=(135, 206, 235)):
        super(Ally, self).__init__(image='img/circle.png')
        self.scale = size/self.height
        self.color = color
        self.position = pos

    def on_mouse_press(self, x, y, buttons, modfiers):
        print(x, y)

class Check_state(Delay):
    def start(self):
        arena = self.target.parent     #type:Arena
        map = arena.map
        map.turn += 1
        if map.turn <= 5:
            if map.check_states():
                self.target.do(sequence(MoveTo(coordinate(map.i, map.j, arena.size), 2), Check_state(1)))
            else:
                self.target.do(Check_state(1))
        else:
            print('gg')


    def stop(self):
        arena = self.target     #type:Arena
        arena.is_event_handler = True



if __name__ == '__main__':
    director.init(caption='3X')
    director.run(cocos.scene.Scene(Arena()))
