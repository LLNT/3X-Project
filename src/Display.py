import cocos
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import MoveTo
from data_loader import Main as Data
from global_vars import Main as Global
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
        map1 = map_controller.Main(terrain_container_test, person_container_test, data)
        self.w = terrain_container_test.N
        self.h = terrain_container_test.M

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

    def move(self, id, x, y):
        s = self.person[id]
        mov = MoveTo((s.position[0], s.position[1]), 2) + MoveTo((x * self.size+self.size//2, y * self.size+self.size//2), 2)

        s.do(mov)


    def repaint(self, map_controller):
        position = map_controller.person_container.position
        army = map_controller.person_container.army
        self.person = {}
        for id in position:
            (y, x) = position[id]
            if army[id] == "Lyn's Army" :
                color = ORANGE
            else:
                color = SKY_BLUE
            self.person[id] = Ally(pos=(x * self.size+self.size//2, y * self.size+self.size//2), color=color, size=self.size)
            self.add(self.person[id])
        self.move('1', 3, 3)


    def on_mouse_motion(self, x, y, buttons, modifiers):
        i, j = coordinate_t(x, y, self.size)
        print(i, j)
        if i in range(0, self.w) and j in range(0, self.h):
            i0, j0 = self.select
            self.tiles[i0][j0].color = self.origin_color
            self.origin_color = self.tiles[i][j].color
            self.tiles[i][j].color = LIGHT_PINK
            self.select = i, j


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

if __name__ == '__main__':
    director.init(caption='3X')
    director.run(cocos.scene.Scene(Arena()))
