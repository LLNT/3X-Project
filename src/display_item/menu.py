# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out
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

class Ordermenu(Menu):
    is_event_handler = True

    def __init__(self, arena):
        super(Ordermenu, self).__init__(title='Order')

        l = []
        l.append(MenuItem('Move', self.move))
        l.append(MenuItem('Attack', self.attack))

        map = arena.map
        pid = arena.selected
        position = arena.target
        self.sup_dict = map.can_support(pid, position)
        if len(self.sup_dict) > 0:
            l.append(MenuItem('Support', self.support))
        self.position = arena.width//2,0
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())

    def on_mouse_release(self, x, y, buttons, modifiers):
        if buttons == 1:
            super().on_mouse_release(x, y, buttons, modifiers)

    def move(self):
        self.parent.move()
        self.parent.remove(self)
        del self

    def cancel(self):
        self.parent.cancel()
        self.parent.remove(self)
        del self

    def attack(self):
        self.parent.attack()
        self.parent.remove(self)
        del self

    def support(self):
        self.parent.support(self.sup_dict)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()


class Weaponselect(Menu):
    is_event_handler = True
    def __init__(self, person, dst, map):
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


class Weaponmenu(Menu):
    is_event_handler = True

    def __init__(self, items, map, arena):
        super(Weaponmenu, self).__init__(title='Weapons')
        w, h = director.get_window_size()
        self.w, self.h = w, h
        l = []
        for item in items:
            if map.attackable(item.itemtype.weapontype):
                l.append(MenuItem(item.itemtype.name, self.iteminfo, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.position = arena.width // 2, 0
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)

    def on_mouse_release(self, x, y, buttons, modifiers):
        if buttons == 1:
            super().on_mouse_release(x, y, buttons, modifiers)

    def iteminfo(self, item):
        content = []
        it = item.itemtype
        content.append('name: ' + it.name)
        content.append('max_use: ' + str(it.max_use))
        content.append('use:' + str(item.use))
        content.append('type: ' + it.weapontype)
        content.append('power: ' + str(it.power))
        content.append('weight: ' + str(it.weight))
        content.append('hit: ' + str(it.hit))
        content.append('critical: ' + str(it.critical))
        content.append('max_range: ' + str(it.max_range))
        content.append('min_range: ' + str(it.min_range))
        info = Info(size=(self.w // 2, self.h), position=(self.w // 2, 0))
        self.parent.add(info)
        info.display(content)
        self.parent.remove(self)
        self.parent.wpinfo = info
        self.parent.select_target(item)


    def cancel(self):
        self.parent.state = 'valid_dst'
        self.parent.menu = Ordermenu(self.parent)
        self.parent.add(self.parent.menu)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()