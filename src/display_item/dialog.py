"""
@version: ??
@author: Antastsy
@time: 18-2-20 
"""

from cocos.layer import Layer, ColorLayer
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import Delay, CallFunc
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
        print('dialog_click at ', self)
        if buttons is 1:
            if self.i < self.length:
                self.excute()
            else:
                self.exit()
        elif buttons is 4:
            while self.i < self.length:
                item = self.textsource[self.textlist[self.i]]
                if 'Branch' in item.keys():
                    self.add(Branch(self.map, item['Branch'], self._callback))
                    director.window.remove_handlers(self)
                    break
                self.i += 1
            if not self.i < self.length:
                self.exit()


    def source_error(self, info):
        print('source error type ' + str(info))

    def _callback(self):
        # handle callback from branches
        if not self.i < self.length:
            print('Finished')
            self.exit()
        else:
            director.window.push_handlers(self)

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

        self.background = Sprite(map.scene, position=(w // 2, h // 2))
        text_background = ColorLayer(0,0,200,255,w,h//3)
        self.add(self.background)
        self.add(text_background)

        # add img
        self.left = Sprite('ring.png', position=(w // 6, h // 2), opacity=0)
        self.right = Sprite('ring.png', position=(w * 5 // 6, h // 2), opacity=0)
        self.add(self.left)
        self.add(self.right)

        # add label
        self.label = Text(text=' ', position=(w // 6, h // 3), font_size=24)
        self.add(self.label)

        # add text
        self.text = Text(text=' ', position=(w // 2, h // 6), font_size=30)
        self.add(self.text)

    def excute(self):
        item = self.textsource[self.textlist[self.i]]
        super().excute()
        if 'Branch' in item.keys():
            self.add(Branch(self.map, item['Branch'], self.callback))
            director.window.remove_handlers(self)
        else:
            if item['Type'] is 'S':
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
                    if item['Tag'] is 'V':
                        self.label.element.text = self.info['V'].name
                    else:
                        self.label.element.text = item['Tag']
                else:
                    self.label.element.text = ''
            elif item['Type'] is 'N':
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
            else:
                self.source_error(item['Type'])

    def changeleft(self, source):
        self.left.kill()
        if type(source) is str:
            self.left = Sprite(source, position=(self.w // 6, self.h // 2))
            self.left.scale_x, self.left.scale_y = \
                480 / self.left.width, 640 / self.left.height
        else:
            self.left = Layer()
            pos1, pos2 = (300, self.h // 2), (640, self.h // 2)
            spr1, spr2 = Sprite(source[0], position=pos1), Sprite(source[1], position=pos2)
            spr1.scale_x, spr1.scale_y = 480 / spr1.width, 640 / spr1.height
            spr2.scale_x, spr2.scale_y = 480 / spr2.width, 640 / spr2.height
            self.left.add(spr1)
            self.left.add(spr2)
        self.add(self.left)

    def changeright(self, source):
        self.right.kill()
        if type(source) is str:
            self.right = Sprite(source, position=(self.w * 5 // 6, self.h // 2))
            self.right.scale_x, self.right.scale_y = \
                480 / self.right.width, 640 / self.right.height
        else:
            self.right = Layer()
            pos1, pos2 = (self.w-640, self.h // 2), (self.w-300, self.h // 2)
            spr1, spr2 = Sprite(source[0], position=pos1), Sprite(source[1], position=pos2)
            spr1.scale_x, spr1.scale_y = 480 / spr1.width, 640 / spr1.height
            spr2.scale_x, spr2.scale_y = 480 / spr2.width, 640 / spr2.height
            self.right.add(spr1)
            self.right.add(spr2)
        self.add(self.right)

    def exit(self):
        self.kill()
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
        try:
            dir = self.pid2dir[item['Speaker']]
        except:
            dir = 'left'

        if dir is 'left':
            self.label['right'].visible = False
            self.label['left'].visible = True
        else:
            self.label['right'].visible = True
            self.label['left'].visible = False
        self.label[dir].element.text = item['Tag']
        self.text.element.text = item['Text']
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
        director.window.remove_handlers(self)
        self.callback.__call__(**self.kwargs)

class Mapdialog(BaseDialog):
    def __init__(self, textlist, textsource, w, h, map, callback, size=(200,200),**kwargs):
        super().__init__(textlist, textsource)

        self.w, self.h = w, h
        self.callback = callback
        self.kwargs = kwargs
        self.size = size
        self.map = map

        self.up = {
            'Icon': Sprite('ring.png', position=(w // 8, h * 3 // 4), opacity=0),
            'Text': Text(text=' ', position=(w // 2, h * 3 // 4),font_size=30, color=(0,0,0,255)),
        }
        self.down = {
            'Icon': Sprite('ring.png', position=(w * 7 // 8, h  // 4), opacity=0),
            'Text': Text(text=' ', position=(w // 2, h  // 4), font_size=30, color=(0,0,0,255)),
        }

        for item in self.up.values():
            self.add(item)
        for item in self.down.values():
            self.add(item)

        self.excute()

    def excute(self):
        if self.i < self.length:
            item = self.textsource[self.textlist[self.i]]
            if 'Branch' in item.keys():
                self.add(Branch(self.map, item['Branch'], self._callback))
                director.window.remove_handlers(self)
                super().excute()
            else:
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
                    obj['Icon'].scale_x = self.size[0] / obj['Icon'].width
                    obj['Icon'].scale_y = self.size[1] / obj['Icon'].height
                    self.add(obj['Icon'])
                obj['Text'].element.text = item['Text']
                super().excute()
        else:
            director.window.remove_handlers(self)
            self.exit()

    def exit(self):
        self.kill()
        self.callback.__call__(**self.kwargs)

class Afterdialog(Dialogscene):
    '''
    def __init__(self, text_list, text_source, map, w, h, info, tag, size=200,
                 left=None, right=None, callback=None, **kwargs):
        super(Dialogscene, self).__init__(text_list, text_source)
        self.map = map
        self.w, self.h = w, h
        self.size = size
        self.callback = callback
        self.kwargs = kwargs
        self.info = info  # dict of persons that stands for V or E

        # add background

        self.background = Sprite(map.scene, position=(w // 2, h // 2))
        text_background = ColorLayer(0, 0, 200, 255, w, h // 3)
        self.add(self.background)
        self.add(text_background)

        # add img
        self.left = Sprite('ring.png', position=(w // 6, h // 2), opacity=0)
        self.right = Sprite('ring.png', position=(w * 5 // 6, h // 2), opacity=0)
        self.add(self.left)
        self.add(self.right)

        # add label
        self.label = Text(text=' ', position=(w // 6, h // 3), font_size=24)
        self.add(self.label)

        # add text
        self.text = Text(text=' ', position=(w // 2, h // 6), font_size=30)
        self.add(self.text)

        self.left_text, self.right_text = None, None
        if left is not None:
            self.changeleft(left)
        if right is not None:
            self.changeright(right)

        if tag is not None:
            self.tag = Text(text=tag, position=(w * 5 // 6, h * 2 // 3), font_size=24)
            self.add(self.tag)

        self.excute()


    def changeleft(self, source):
        super().changeleft(source)
        self.left_text = source

    def changeright(self, source):
        super().changeright(source)
        self.right_text = source
    '''
