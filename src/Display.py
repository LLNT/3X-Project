import cocos
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import MoveTo
from data_loader import Main as Data
from global_vars import Main as Global
from terrain_container import Main as Terrain_Container
from person_container import Main as Person_Container
import map_controller
from colors import *
class Arena(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        self.size = 80
        data = Data()
        global_vars = Global(data)
        terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
        person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
        map1 = map_controller.Main(terrain_container_test, person_container_test, data)
        w = terrain_container_test.N
        h = terrain_container_test.M

        super(Arena, self).__init__(r=0,g=0,b=0,a=255,width=w*self.size,height=h*self.size)
        for x in range(w):
            for y in range(h):
                self.add(Tile(pos=(x * self.size+self.size//2, y * self.size+self.size//2), color=(255, 255, 255), size=self.size))
        self.repaint(map1)

    def transform_xy(self, x, y):
        pass

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




class Tile(Sprite):
    def __init__(self, size=50,pos=None):
        super(Tile, self).__init__(image='img/circle.png')
        self.scale = size/self.height
        self.color = (255, 255, 255)
        self.position = pos



class Ally(Sprite):
    def __init__(self, size=50,pos=None, color=(135, 206, 235)):
        super(Tile, self).__init__(image='img/circle.png')
        self.scale = size/self.height
        self.color = color
        self.position = pos

    def on_mouse_press(self, x, y, buttons, modfiers):
        print(x, y)

if __name__ == '__main__':
    director.init(caption='3X')
    director.run(cocos.scene.Scene(Arena()))
