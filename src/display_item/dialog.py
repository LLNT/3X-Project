"""
@version: ??
@author: Antastsy
@time: 18-2-20 
"""

from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.director import director
from typing import List, Dict
from map_controller import Main
from display_item.text import Text
from cocos.text import RichLabel
from cocos.menu import Menu, MenuItem

class BaseDialog(Layer):

    is_event_handler = True

    def __init__(self, textlist, textsource):
        super().__init__()
        self.textlist = textlist        #type:List[str]
        self.textsource = textsource    #type:Dict[str,Dict[str,str]]
        self.length = len(textlist)
        self.i = 0

    def excute(self):
        # print(self.textsource[self.textlist[self.i]])
        self.i += 1

    def exit(self):
        pass

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.i < self.length:
            self.excute()
        else:
            self.exit()

    def source_error(self, info):
        print('source error type ' + str(info))

class Dialogscene(BaseDialog):

    def __init__(self, text_list, text_source, map, w, h, info,
                 size=200, callback=None, **kwargs):

        super().__init__(text_list, text_source)
        self.map = map
        self.w, self.h = w, h
        self.size = size
        self.callback = callback
        self.kwargs = kwargs
        self.info = info # dict of persons that stands for V or E

        # add background
        background = Sprite('background_test.jpg', position=(w // 2, h // 2))
        text_background = ColorLayer(0,0,200,255,w,h//3)
        self.add(background)
        self.add(text_background)

        # add img
        self.left = Sprite('ring.png', position=(w // 6, h // 2))
        self.right = Sprite('ring.png', position=(w * 5 // 6, h // 2))
        self.add(self.left)
        self.add(self.right)

        # add label
        self.label = Text(text=' ', position=(w // 6, h // 3), font_size=24)
        self.add(self.label)

        # add text
        self.text = Text(text=' ', position=(w // 2, h // 6), font_size=30)
        self.add(self.text)

        self.excute()

    def excute(self):
        item = self.textsource[self.textlist[self.i]]
        if item['Type'] is not 'S':
            self.source_error('S')
        if 'Branch' in item.keys():
            self.add(Branch(self.map, item['Branch'], self.excute))
            director.window.remove_handlers(self)
            self.i += 1
        else:

            if item['Text'] is not None:
                self.text.element.text = item['Text']
            if item['Left'] is not None:
                if item['Left'] is 'V':
                    item['Left'] = self.info['V'].pic
                self.changeleft(item['Left'])
            if item['Right'] is not None:
                if item['Right'] is 'V':
                    item['Right'] = self.info['V'].pic
                self.changeright(item['Right'])
            if item['Direction'] == 0:
                self.label.position = (self.w // 6, self.h // 3)
            else:
                self.label.position = (self.w * 5 // 6, self.h // 3)
            if item['Tag'] is not None:
                self.label.element.text = item['Tag']
            super().excute()

    def changeleft(self, source):
        self.left.kill()
        self.left = Sprite(source, position=(self.w // 6, self.h // 2))
        self.left.scale_x, self.left.scale_y = \
            self.size / self.left.width, self.size / self.left.height
        self.add(self.left)

    def changeright(self, source):
        self.right.kill()
        self.right = Sprite(source, position=(self.w * 5 // 6, self.h // 2))
        self.right.scale_x, self.right.scale_y = \
            self.size / self.right.width, self.size / self.right.height
        self.add(self.right)

    def exit(self):
        director.pop()
        if self.callback:
            self.callback.__call__(**self.kwargs)

class Battledialog(BaseDialog):

    def __init__(self, textlist, textsource, w, h, dialog_info, callback, **kwargs):
        super().__init__(textlist, textsource)

        self.w, self.h = w, h
        self.pid2dir = dialog_info['pid2dir']
        self.callback = callback
        self.kwargs = kwargs

        # add label
        self.text = Text(text=' ', position=(w // 2, h // 6), font_size=30)
        self.add(self.text)

        # add text
        self.label = {}
        self.label['left'] = Text(text=' ', position=(w // 4, h // 4),font_size=25)
        self.label['right'] = Text(text=' ', position=(w * 3 // 4, h // 4), font_size=25)
        self.add(self.label['left'])
        self.add(self.label['right'])
        self.excute()

    def excute(self):
        item = self.textsource[self.textlist[self.i]]
        dir = self.pid2dir[item['Speaker']]
        self.label[dir].element.text = item['Tag']
        self.text.element.text = item['Text']
        if dir is 'left':
            self.label['right'].visible = False
            self.label['left'].visible = True
        else:
            self.label['right'].visible = True
            self.label['left'].visible = False

        super().excute()

    def exit(self):
        self.kill()
        self.callback.__call__(**self.kwargs)

    pass

class Branch(Menu):
    is_event_handler = True

    def __init__(self, map, branches, callback, **kwargs):

        super().__init__()
        l = []
        self.callback = callback
        self.kwargs = kwargs
        self.map = map
        for branch in branches:
            text = branch['Text']
            flag = branch["Flag"]
            l.append(MenuItem(text, self.action, flag))

        self.create_menu(l, None, None)

    def action(self, flag):
        self.map.global_vars.flags[flag] = True
        for obj in self.children_names:
            self.remove(obj)

        self.kill()
        self.callback.__call__(**self.kwargs)
        director.window.push_handlers(self.parent)

class Mapdialog(BaseDialog):
    def __init__(self, textlist, textsource, w, h, dialog_info, callback, **kwargs):
        super().__init__(textlist, textsource)

        self.w, self.h = w, h
        self.callback = callback
        self.kwargs = kwargs

        self.up = {
            'Icon': Sprite('ring.png', position=(w // 8, h * 3 // 4), opacity=0),
            'Text': Text(text=' ', position=(w // 2, h * 3 // 4),font_size=30),
        }
        self.down = {
            'Icon': Sprite('ring.png', position=(w * 7 // 8, h  // 4), opacity=0),
            'Text': Text(text=' ', position=(w // 2, h  // 4), font_size=30),
        }

        for item in self.up.values():
            self.add(item)
        for item in self.down.values():
            self.add(item)

        self.excute()

    def excute(self):
        item = self.textsource[self.textlist[self.i]]
        if item['Type'] is not 'M':
            self.source_error('M')
        if item['Location'] is 0:
            obj = self.up
        elif item['Location'] is 1:
            obj = self.down
        else:
            self.source_error('Location')
            return
        pos = obj['Icon'].position
        obj['Icon'].kill()
        if item['Icon'] is not None:
            obj['Icon'] = Sprite(item['Icon'], pos)
            self.add(obj['Icon'])
        obj['Text'].element.text = item['Text']
        super().excute()

    def exit(self):
        self.kill()
        self.callback.__call__(**self.kwargs)