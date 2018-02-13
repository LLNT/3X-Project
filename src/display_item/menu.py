# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out
from display_item.info import Info
from cocos.director import director
from cocos.layer import ColorLayer
class Menulayer(ColorLayer):
    def __init__(self):
        w, h = director.get_window_size()
        super().__init__(0,0,0,200,w//4, h)
        self.position = w - w //4, 0
        self.opacity = 0

    def appear(self, opcacity=200):
        self.opacity = 200

    def disapper(self):
        self.opacity = 0


class Ordermenu(Menu):
    is_event_handler = True

    def __init__(self, arena):
        super(Ordermenu, self).__init__(title='Order')
        self.arena = arena
        l = []
        l.append(MenuItem('Move', self.move))
        l.append(MenuItem('Attack', self.attack))
        l.append(MenuItem('Item', self.item))

        map = arena.map
        pid = arena.selected
        position = arena.target

        self.avl = map.available_wand(pid)
        if len(self.avl) > 0:
            l.append(MenuItem('Wand', self.wand))

        self.sup_dict = map.can_support(pid, position)
        if len(self.sup_dict) > 0:
            l.append(MenuItem('Support', self.support))

        self.exc = arena.can_exchange(position)
        if len(self.exc) > 0:
            l.append(MenuItem('Exchange', self.exchange))

        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.position = - director.get_window_size()[0] * 3 // 8, 0


    def on_mouse_release(self, x, y, buttons, modifiers):
        if buttons == 1:
            super().on_mouse_release(x, y, buttons, modifiers)

    def move(self):
        self.arena.move()
        self.parent.remove(self)
        del self

    def cancel(self):
        self.arena.cancel()
        self.parent.remove(self)
        del self

    def attack(self):
        self.arena.attack()
        self.parent.remove(self)
        del self

    def wand(self):
        self.arena.wand(self.avl)
        self.parent.remove(self)
        del self

    def support(self):
        self.arena.support(self.sup_dict)
        self.parent.remove(self)
        del self

    def item(self):
        self.arena.item_show()
        self.parent.remove(self)
        del self

    def exchange(self):
        self.arena.exchange(self.exc)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Showwand(Menu):
    is_event_handler = True

    def __init__(self, avl, arena):
        super().__init__(title='Wands')
        w, h = director.get_window_size()
        self.w, self.h = w, h
        l = []
        for item in avl:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.wanduse, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)
        self.position = - director.get_window_size()[0] * 6 // 8, 0
        self.arena = arena

    def wanduse(self, item):
        self.parent.remove(self)
        self.arena.wanduse(item)

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(self.arena.menu)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Showweapon(Menu):
    is_event_handler = True

    def __init__(self, items, arena):
        super(Showweapon, self).__init__(title='Weapons')
        w, h = director.get_window_size()
        self.w, self.h = w, h
        l = []
        for item in items:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.itemuse, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)
        self.position = - director.get_window_size()[0] * 6 // 8, 0
        self.arena = arena

    def itemuse(self, item):
        self.parent.remove(self)
        self.parent.add(Itemuse(item, self, self.arena))

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(self.arena.menu)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Itemuse(Menu):
    is_event_handler = True

    def __init__(self, item, menu, arena):
        super().__init__(title='Weapons')
        w, h = director.get_window_size()
        self.w, self.h = w, h
        l = []
        pid = arena.selected
        map = arena.map
        if map.can_use(pid, item):
            l.append(MenuItem('Use', self.use))
        if map.can_equip(pid, item):
            l.append(MenuItem('Equip', self.equip))
        if map.can_banish(pid, item):
            l.append(MenuItem('Banish', self.banish))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)
        self.position = - director.get_window_size()[0] * 3 // 8, 0
        self.item = item
        self.menu = menu
        self.arena = arena

    def use(self):
        self.arena.use(self.item)
        self.parent.remove(self)
        pass

    def equip(self):
        self.arena.equip(self.item)
        self.parent.remove(self)
        pass

    def banish(self):
        self.arena.banish(self.item)
        self.parent.remove(self)
        pass

    def cancel(self):
        self.parent.remove(self)
        self.parent.add(self.menu)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

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
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)
        self.position = - director.get_window_size()[0] * 3 // 8, 0
        self.arena = arena

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
        self.arena.add(info)
        info.display(content)
        self.parent.remove(self)
        self.arena.wpinfo = info
        self.arena.select_target(item)


    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(self.arena.menu)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Weaponexchange(Menu):
    is_event_handler = True

    def __init__(self, items, arena, position):
        super(Weaponexchange, self).__init__()
        w, h = director.get_window_size()
        self.w, self.h = w, h
        l = []
        for item in items:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.item, item))
        if len(l) < 5:
            l.append(MenuItem('Empty', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        # self.position = (-w // 4, 0)
        self.position = position
        self.arena = arena

    def item(self, item):
        self.cancel()

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(self.arena.menu)
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Endturn(Menu):
    is_event_handler = True
    def __init__(self, arena):
        super().__init__(title='Endturn')
        l = []
        l.append(MenuItem('Endturn', self.end_turn))
        l.append(MenuItem('Cancel', self.cancel))

        self.position = - director.get_window_size()[0] * 3 // 8, 0
        self.create_menu(l, zoom_in(), zoom_out())
        self.arena = arena

    def cancel(self):
        self.arena.is_event_handler = True
        self.parent.remove(self)
        del self

    def end_turn(self):
        self.arena.end_turn()
        self.parent.remove(self)
        del self

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()
