"""
@version: ??
@author: Antastsy
@time: 2018/5/3 22:24
"""
from cocos.layer import ColorLayer
from .text import Text

class Turn(ColorLayer):

    def __init__(self, title, turn, w=800, h=600):

        super().__init__(100,100,100,100, w, h)

        self.text2 = Text(text='Turn %s'%turn, position=(w // 2, h * 3 // 7), font_size=30)
        self.add(self.text2)
        self.text1 = Text(text=title, position=(w // 2, h * 4 // 7), font_size=30)
        self.add(self.text1)

class Chapter(ColorLayer):

    def __init__(self, title, w=800, h=600):

        super().__init__(100,100,100,100, w, h)

        self.text1 = Text(text=title, position=(w // 2, h //2), font_size=30)
        self.add(self.text1)


if __name__ == '__main__':
    pass
