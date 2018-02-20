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



class Dialogscene(BaseDialog):

    def __init__(self, arena, w, h):
        map = arena.map #type:Main
        textsource = map.global_vars.text
        textlist = arena.textlist
        super().__init__(textlist, textsource)
        self.w, self.h = w, h

        # add background
        background = Sprite('background_test.jpg', position=(w // 2, h // 2))
        textbackground = ColorLayer(0,0,200,255,w,h//3)
        self.add(background)
        self.add(textbackground)

        # add img
        self.left = Sprite('ring.png', position=(w // 6, h // 2))
        self.right = Sprite('ring.png', position=(w * 5 // 6, h // 2))
        self.add(self.left)
        self.add(self.right)

        # add label
        self.label = Text('', (w // 6, h // 3))
        self.add(self.label)

        # add text
        self.text = Text('', (w // 2, h // 6))
        self.add(self.text)

        self.excute()

    def excute(self):
        item = self.textsource[self.textlist[self.i]]
        if item['Text'] is not None:
            self.text.element.text = item['Text']
        if item['Left'] is not None:
            self.changeleft(item['Left'])
        if item['Right'] is not None:
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
        self.left.scale_x, self.left.scale_y = 200 / self.left.width, 200 / self.left.height
        self.add(self.left)

    def changeright(self, source):
        self.right.kill()
        self.right = Sprite(source, position=(self.w * 5 // 6, self.h // 2))
        self.right.scale_x, self.right.scale_y = 200 / self.right.width, 200 / self.right.height
        self.add(self.right)

    def exit(self):
        director.pop()

    pass

if __name__ == '__main__':
    pass