# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 19:03
'''
from cocos.sprite import Sprite
from cocos.text import RichLabel
from utility import coordinate
from cocos.director import director
import pyglet

class Cell(Sprite):
    def __init__(self, size=50,pos=(0, 0),state='default',path='sprite/red.png',color=(255, 255, 255)):
        '''

        :param size: fixed size of every cell's length and width
        :param pos:  position of the cell, should be transformed to the pixel position of left_down
        :param state:  record state includes default, with person on, target
        :param path: resource file path
        :param color:
        '''
        super(Cell, self).__init__(image=path)
        self.scale = size/self.height
        self.color = color
        self.position = coordinate(pos[0], pos[1], size)
        self.state = state
        self.person_on = None
        self.opacity = 0
        self.size = size

    def change_source(self, source='blue', opacity=255):
        img = 'sprite/' + source + '.png'
        self._set_texture(pyglet.resource.image(img).get_texture())
        self.opacity = opacity


class Charactor(Sprite):
    def __init__(self, person, scale=1,size=50,pos=(0, 0),controller=0,state='unmoved',
                 path='ring.png',color=(255, 255, 255)):
        '''

        :param pid: pid of person object this sprite refers to
        :param size: arena's size used to confirm positions
        :param scale: you have known what that means
        :param pos:  position of the cell, should be transformed to the pixel position of left_down
        :param state:  record state includes default, with person on, target
        :param path: resource file path
        :param color:
        '''
        super(Charactor, self).__init__(image=path)
        self.scale = scale * size / self.height
        self.color = color
        self.position = coordinate(pos[0], pos[1], size)
        self.controller = controller
        self.state = state
        self.person = person
        self.pid = person.pid
        self.pos = pos

    def on_enter(self):
        super().on_enter()
        director.window.push_handlers(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        print(x, y, modifiers)
        if self.contains(x, y):
            print(1)

class Button(Sprite):
    selected_effect = None
    unselected_effect = None
    activated_effect = None

    def __init__(self, label, scale=1,pos=(0, 0), anchor=None, path='ring.png', color=(255, 255, 255),
                 font_size=30, font_color=(127, 255, 170, 255)):

        super().__init__(image=path,position=pos,color=color, scale=scale, anchor=anchor)


        self.activated = False
        self.selected =False
        self.radius = self.height / 2
        text = RichLabel(label, (0, 0), anchor_x='center', anchor_y='center',
                         font_size=font_size, color=font_color)
        self.add(text)

    def on_mouse_motion(self, x, y, buttons, modifiers):
        if (x - self.position[0]) ** 2 + (y - self.position[1]) ** 2 < self.radius ** 2:
            self.on_selected()
        else:
            self.on_unselected()

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 1 and self.selected:
            self.on_activated()

    def on_enter(self):
        super().on_enter()
        director.window.push_handlers(self)

    def on_exit(self):
        super().on_exit()
        director.window.remove_handlers(self)

    def on_selected(self):
        if self.selected_effect:
            self.stop()
            self.do(self.selected_effect)

    def on_unselected(self):
        if self.unselected_effect:
            self.stop()
            self.do(self.unselected_effect)

    def on_activated(self):
        if self.activated_effect:
            self.stop()
            self.do(self.activated_effect)

class Endturn(Button):
    def on_selected(self):
        self.color = (255, 215, 0)
        self.selected = True

    def on_unselected(self):
        self.color = (128, 0, 0)
        self.selected = False

    def on_activated(self):
        if self.parent.state is 'default':
            self.parent.end_turn()


class Cursor(Sprite):
    
    def __init__(self, size=80):
        super().__init__('sprite/cursor.png')
        self.scale_y, self.scale_x = size / self.height, size / self.width
        self.image_anchor = (0, 0)
