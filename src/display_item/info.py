from display_item.bar import Bar, Scale_to
from person import Person
from cocos.sprite import Sprite
from cocos.director import director
from cocos.layer import ColorLayer
from display_item.text import layout
from cocos.actions import CallFunc, Delay
from battle import Battle

class Info(ColorLayer):

    def __init__(self, size=None, position=None, center=False, color=(200,200,200), alpha=200):
        '''

        :param size: the size of info layer, equals to the director if none
        :param position: the position of the left_down, equals to 0, 0 if none
        '''

        width, height = director.get_window_size()
        if size is None:
            w, h = width, height
        else:
            w, h = size

        super(Info, self).__init__(r=color[0],g=color[1],b=color[2],a=alpha,width=w, height=h)
        if center:
            self.position = (width - w) / 2, (height - h) / 2
        else:
            if position is not None:
                self.position = position
            else:
                self.position = 0, 0
        self.contents = {}

    def display(self, content, pos_range=None, font_size=30, contentid=None):
        if pos_range is None:
            items = layout(content, ((0, 0),
                                          (self.width, self.height)), font_size=font_size)
        else:
            items = layout(content, pos_range, font_size=font_size)
        for item in items:
            self.add(item)
        if contentid:
            self.contents[contentid] = items
        else:
            self.contents[len(self.contents)] = items

    def info_clear(self, contentid=None):
        if contentid:
            if contentid in self.contents.keys():
                for item in self.contents[contentid]:
                    self.remove(item)
                del self.contents[contentid]
            else:
                pass
        else:
            self.parent.remove(self)
            del self

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
        self.spr.position = self.width*1//4, self.height*3//4
        self.add(self.spr)

        content = []
        content.append('HP:' + str(p.ability['HP']))
        content.append('MHP:' + str(p.ability['MHP']))
        self.display(content, ((0, 0), (self.width//2, self.height//2)))
        content = []
        for item in p.item:
            content.append(str(item.use) + '/' + str(item.itemtype.max_use))
            content.append(item.itemtype.name)

        self.display(content, ((self.width//2, 0), (self.width, self.height)))


class Battleinfo(Info):
    def __init__(self, at, df, wp, map, pos):
        super(Battleinfo, self).__init__()
        self.info_display(at, df, wp, map, pos)
        self.battle_element = [at, df, wp, map, pos]


    def info_display(self, at, df, wp, map, pos):
        wp_d = df.item[0]
        self.battle = Battle(at, df, wp, wp_d, map, pos)
        res = self.battle.simulate()
        content = []
        content.append('sup: ' + str(res[1]))
        content.append('pur: ' + str(res[2]))
        content.append('hit: ' + str(res[3]))
        content.append('crt: ' + str(res[4]))
        content.append('dmg: ' + str(res[5]))
        self.display(content, ((0, self.height / 2), (self.width / 2, self.height)))

        if res[0] == 0:
            content = []
            content.append('sup: ' + str(res[6]))
            content.append('pur: ' + str(res[7]))
            content.append('hit: ' + str(res[8]))
            content.append('crt: ' + str(res[9]))
            content.append('dmg: ' + str(res[10]))
            self.display(content, ((self.width / 2, self.height / 2), (self.width, self.height)))

        else:
            self.display(['No reflection'], ((self.width / 2, self.height / 2), (self.width, self.height)))

class Experience(Info):
    def __init__(self, **kwargs):
        w, h = director.get_window_size()
        if 'width' in kwargs.keys() and 'height' in kwargs.keys():
            width = kwargs['width']
            height = kwargs['height']
        else:
            width, height = w//2, h//2
        if 'position' in kwargs.keys():
            pos = kwargs['position']
        else:
            pos = (0, 0)


        super().__init__(size=(width, height), center=True, alpha=255)
        print(kwargs)
        self.growthlist = kwargs['growthlist']
        self.origin = kwargs['origin']
        self.level = kwargs['level']
        self.person = kwargs['person']
        self.leftexp = kwargs['exp']
        oriexp = self.origin['EXP']

        self.abilities = ["MHP","STR","MGC","SPD","SKL","DEF","RES","LUK"]
        if self.level > 0:
            content_label = []
            for ability in self.abilities:
                content_label.append(ability + ':  ')
            content_label.append('')
            self.display(content_label, font_size=24, pos_range=((0, 0), (self.width // 3, self.height)))
        else:
            self.opacity = 0
        self.bar = Bar(size=(self.width, 30), prop=oriexp / 100, position=(0, -40), color=(0, 0, 255))
        self.add(self.bar)
        self.i = 0
        self.flag = True
        
    def on_enter(self):
        super().on_enter()
        self.bar_raise()

    def bar_raise(self, duration=3):
        if self.bar.scale_x == 1:
            self.bar.scale_x = 0
        if self.i < self.level:
            d = duration * (1 - self.bar.scale_x)
            scale = 1
        else:
            scale = self.leftexp / 100
            d = duration * (scale - self.bar.scale_x)
        self.bar.do(Scale_to(scale_x=scale, scale_y=1, duration=d) + CallFunc(self.level_up))

    def level_up(self):
        if self.i == self.level:
            if self.flag:
                print(self.parent)
                director.window.push_handlers(self.parent)
                self.flag = False
                del self
            return
        self.info_clear(1)
        self.info_clear(2)
        self.info_clear(3)
        
        content_origin = []
        for ability in self.abilities:
            content_origin.append(str(self.origin[ability]))
        content_origin.append('Origin')
        self.display(content_origin, font_size=20, contentid=1,
                     pos_range=((self.width // 3, 0), (self.width * 5 // 9, self.height)))
        growth = self.growthlist[self.i]
        content_grow = []
        for ability in self.abilities:
            content_grow.append(str(growth[ability]))
        content_grow.append('Grow')
        self.display(content_grow, font_size=20, contentid=2,
                     pos_range=((self.width*5//9, 0), (self.width*7//9, self.height)))
        content_new = []
        for ability in self.abilities:
            self.origin[ability] = growth[ability] + self.origin[ability]
            content_new.append(str(self.origin[ability]))
        content_new.append('New')
        self.display(content_new, font_size=20, contentid=3,
                     pos_range=((self.width *7//9, 0), (self.width, self.height)))


        self.do(Delay(0.5) + CallFunc(self.bar_raise))
        self.i += 1

