import cocos
from person import Person
from cocos.sprite import Sprite
from cocos.director import director
class Info(cocos.layer.ColorLayer):
    is_event_handler = True
    def __init__(self):
        w, h = director.get_window_size()
        super(Info, self).__init__(r=255, g=255, b=255, a=255, width=w, height=h)
        self.visible = False


    def info_display(self, person):
        p = person #type: Person
        self.spr = Sprite(image=p.pic)
        h = self.spr.height
        w = self.spr.width
        self.spr.scale_x, self.spr.scale_y = self.width/(w*2), self.height/(h*2)
        self.spr.position = self.width*1/4, self.height*3/4
        self.add(self.spr)
        self.visible = True
        self.name = Text(p.name,(self.width*3/4, self.height*3/4))
        self.add(self.name)
        hp = str(p.ability['HP'])
        self.hp = Text('HP:'+hp,(self.width*1/4, self.height*3/8))
        mhp = str(p.ability['MHP'])
        self.mhp = Text('MHP:' + mhp,(self.width*1/4, self.height*1/8))
        self.add(self.hp)
        self.add(self.mhp)

    def info_clear(self):
        self.remove(self.spr)
        self.remove(self.name)
        self.remove(self.hp)
        self.remove(self.mhp)
        self.visible = False

class Text(cocos.text.RichLabel):

    def __init__(self, content, position, color=(127, 255, 170, 255),
                 font_name='times new roman',font_size=36):
        super(Text, self).__init__(text=content,
                                   font_name=font_name,
                                   font_size=font_size,
                                   position=position,
                                   color=color,
                                   anchor_x='center',
                                   anchor_y='center')


