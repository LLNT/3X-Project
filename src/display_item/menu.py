# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, verticalMenuLayout
from display_item.info import Info
from cocos.director import director

class Optionmenu(Menu):
    is_event_handler = True
    def __init__(self, person, dst):
        super(Optionmenu, self).__init__(title='options')
        l = []
        l.append(MenuItem('Move', self.move))
        l.append(MenuItem('Attack', self.attack))
        l.append(MenuItem('Cancel', self.cancel))

        self.create_menu(l, zoom_in(), zoom_out())
        self.person = person
        self.dst = dst




    def move(self):
        self.parent.move(self.person, self.dst)
        self.parent.remove(self)

    def cancel(self):
        self.parent.remove(self)
        self.parent.choose_new_target()

    def attack(self):
        self.parent.add(Weaponselect(self.person, self.dst))
        self.parent.remove(self)



class Weaponselect(Menu):
    is_event_handler = True
    def __init__(self, person, dst):
        super(Weaponselect, self).__init__(title='Weapons')
        w, h = director.get_window_size()
        self.w, self.h = w, h


        self.person = person
        items = self.person.item
        l = []
        for item in items:
            l.append(MenuItem(item.itemtype.name, self.iteminfo, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.dst = dst
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        self.position = (-w//4, 0)

    def eff(self):
        print(1)

    def iteminfo(self, item):
        content = []

        it = item.itemtype
        content.append('name: ' + it.name)
        content.append('max_use: ' + str(it.max_use))
        content.append('type: ' + it.weapontype)
        content.append('power: ' + str(it.power))
        content.append('weight: ' + str(it.weight))
        content.append('hit: ' + str(it.hit))
        content.append('critical: ' + str(it.critical))
        content.append('max_range: ' + str(it.max_range))
        content.append('min_range: ' + str(it.min_range))
        self.info = Info(size=(self.w//2, self.h),position=(self.w//2, 0))
        self.parent.add(self.info)
        self.info.display(content)
        self.parent.select_attack(self.person, self.dst, item)
        self.parent.remove(self)
        self.parent.info = self.info

    def cancel(self):
        if self.info is not None:
            self.info.clear()
        self.parent.remove(self)
        self.parent.item = None
        self.parent.add(Optionmenu(self.person, self.dst))