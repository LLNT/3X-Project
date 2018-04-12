"""
@version: ??
@author: Antastsy
@time: 18-4-12 下午1:49
"""
from cocos.layer import ColorLayer, Layer
from cocos.scene import Scene
from cocos.scenes import FadeTransition
from cocos.director import director
from global_vars import Main as Global
from display_item.menu import Menulayer
from display_item import arena
from person import Person

class Main(ColorLayer):

    def __init__(self, width, height, arena,
                 operation='save', max_save=4, margin=20):
        '''
        This is the placeholder of all saves
        :param operation: save or load action
        :param max_save: max saves display on screen
        '''
        super().__init__(100,100,100,200,width,height)
        map_list = Global.saved_data_preload()
        w, h = width, height//max_save
        saves = []
        for i in range(max_save):
            save = Save(w, h, map_list[i],operation, margin, arena, i)
            self.add(save)
            save.position = (0, height - h*(i+1)+margin)
            saves.append(save)

        pass

class Save(ColorLayer):
    is_event_handler = True
    def __init__(self, width, height, map, operation, margin, arena, i):
        super().__init__(100,180,100,255, width, height-margin*2)
        self.i = i
        self.arena = arena
        self.operation = operation
        self.map = None
        if map is not None:
            hero = map[0].global_vars.personBank["1"] #type:Person
            self.displayitem=[
                hero.ability['LV'],
                hero.cls,
                map[0].title,
                map[0].global_vars.saved_time,
                map[0].global_vars.saved_type
            ]
            self.map = map[0] 
        else:
            self.displayitem = 'Empty Save'

    def on_mouse_motion(self, x, y, buttons, modifiers):
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons is 1:
            if y in range(self.position[1], self.position[1]+self.height):
                print(self.i, self.displayitem)
                if self.operation is 'save' and self.map is None:
                    print('saved')
                    self.map = self.arena.map
                    self.map.global_vars.map_save(fname='game_%d.sav'%self.i)
                    hero = self.map.global_vars.personBank["1"]  # type:Person
                    self.displayitem = [
                        hero.ability['LV'],
                        hero.cls,
                        self.map.title,
                        self.map.global_vars.saved_time,
                        self.map.global_vars.saved_type
                    ]
                elif self.operation is 'load' and self.map is not None:
                    map = self.map
                    menulayer = Menulayer()
                    infolayer = Layer()
                    arena2 = arena.Arena(map, menulayer, infolayer)

                    class Transition(FadeTransition):
                        def finish(self):
                            super().finish()
                            for rec in map.reconstruct_log:
                                arena2.reconstruct(rec, ty='load')
                            arena2.map.take_turn(arena2)

                    self.kill()
                    director.replace(Transition(Scene(arena2, menulayer, infolayer), duration=1))
                    if self.arena is not None:
                        self.arena.kill()

        elif buttons is 4:
            self.parent.kill()
            if self.arena is not None:
                director.window.push_handlers(self.arena)
            else:
                from main_display import Main
                from display_item.arena import map_init
                layer = Layer()
                director.replace(Scene(layer, Main(map_init(), layer)))
            pass

if __name__ == '__main__':
    pass