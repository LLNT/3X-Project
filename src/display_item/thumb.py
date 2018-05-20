"""
@version: ??
@author: Antastsy
@time: 2018/5/19 17:02
"""

from cocos.layer import ColorLayer
from cocos.batch import BatchNode
from cocos.sprite import Sprite

class Thumb(ColorLayer):

    def __init__(self, minimap, w, h, size=10):
        super().__init__(0,0,0,100,w*size, h*size)
        self.batch = BatchNode()
        for (i, j) in minimap:
            tmp = minimap[(i, j)]
            if tmp is not -1:
                img = 'grid/' + str(tmp) + '.png'
                pos = i*size, j*size
                spr = Sprite(image=img, position=pos)
                spr.scale_x, spr.scale_y = size/spr.width, size/spr.height
                spr.image_anchor = (0, 0)
                self.batch.add(spr)

        self.add(self.batch)
        self.frame = ColorLayer(0,0,100,100,min(w*10, 160), min(h*10, 90))
        self.add(self.frame)

    def update(self, x, y):
        self.frame.position = -x//8, -y//8
        pass


if __name__ == '__main__':
    pass