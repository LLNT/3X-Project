import cocos
from person import Person
from cocos.sprite import Sprite
from cocos.director import director
from cocos.layer import ColorLayer
from display_item.text import layout
from battle import Battle

class Info(ColorLayer):

    def __init__(self, size=None, position=None, center=False):
        '''

        :param size: the size of info layer, equals to the director if none
        :param position: the position of the left_down, equals to 0, 0 if none
        '''

        width, height = director.get_window_size()
        if size is None:
            w, h = width, height
        else:
            w, h = size

        super(Info, self).__init__(200,200,200,200,w, h)
        if center:
            self.position = (width - w) / 2, (height - h) / 2
        else:
            if position is not None:
                self.position = position
            else:
                self.position = 0, 0


    def display(self, content, pos_range=None):
        if pos_range is None:
            self.items = layout(content, ((0, 0),
                                          (self.width, self.height)))
        else:
            self.items = layout(content, pos_range)
        for item in self.items:
            self.add(item)

    def info_clear(self):
        for item in self.items:
            self.remove(item)
        self.parent.remove(self)

class Personinfo(Info):
    # 显示个人的信息
    def __init__(self, person):
        super(Personinfo, self).__init__()
        self.person = person
        self.info_display(person)

    def info_display(self, person):
        p = person #type: Person
        self.spr = Sprite(image=p.pic)
        h, w = self.spr.height, self.spr.width
        self.spr.scale_x, self.spr.scale_y = self.width/(w*2), self.height/(h*2)
        self.spr.position = self.width*1/4, self.height*3/4
        self.add(self.spr)

        content = []
        content.append('HP:' + str(p.ability['HP']))
        content.append('MHP:' + str(p.ability['MHP']))
        self.display(content, ((0, 0), (self.width/2, self.height/2)))

class Battleinfo(Info):
    def __init__(self, at, df, wp, map):
        super(Battleinfo, self).__init__()
        self.info_display(at, df, wp, map)

    def info_display(self, at, df, wp, map):
        wp_d = df.item[0]
        battle = Battle(at, df, wp, wp_d, map)
        res = battle.simulate()
        content = []
        content.append('sup: ' + str(res[1]))
        content.append('pur: ' + str(res[2]))
        content.append('hit: ' + str(res[3]))
        content.append('crt: ' + str(res[4]))
        content.append('dmg: ' + str(res[5]))
        self.display(content, ((0, self.height / 2), (self.width / 2, self.height)))

        if res[1] == 0:
            content = []
            content.append('sup: ' + str(res[6]))
            content.append('pur: ' + str(res[7]))
            content.append('hit: ' + str(res[8]))
            content.append('crt: ' + str(res[9]))
            content.append('dmg: ' + str(res[10]))
            self.display(content, ((self.width / 2, self.height / 2), (self.width, self.height)))

        else:
            self.display(['No reflection'], ((self.width / 2, self.height / 2), (self.width, self.height)))
