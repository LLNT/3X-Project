# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out, ToggleMenuItem, shake
from .info import Info
from cocos.director import director
from cocos.layer import ColorLayer, Layer
from cocos.actions import Delay, CallFunc
from .. import map_controller
from cocos.layer import PythonInterpreterLayer

class Menulayer(Layer):
    def __init__(self):
        super().__init__()
        w, h = director.get_window_size()
        self.menu_back = ColorLayer(0,0,0,200,w//4, h)
        self.menu_back.opacity = 0
        self.add(self.menu_back)

    def appear(self, opcacity=200):
        self.menu_back.opacity = opcacity

    def disapper(self):
        self.menu_back.opacity = 0

    def remove(self, obj):
        super().remove(obj)
        del obj

class Ordermenu(Menu):
    is_event_handler = True

    def __init__(self, arena):
        super(Ordermenu, self).__init__(title='Order')
        self.arena = arena
        map = arena.map  #type:map_controller.Main
        pid = arena.selected
        position = arena.target

        l = []
        l.append(MenuItem('Move', self.move))
        atk = map.find_attackable(pid, position)
        if len(atk) > 0:
            l.append(MenuItem('Attack', self.attack))

        if len(map.global_vars.personBank[pid].item) > 0:
            l.append(MenuItem('Item', self.item))

        self.avl = map.available_wand(pid)
        if len(self.avl) > 0:
            l.append(MenuItem('Wand', self.wand))

        self.sup_dict = map.can_support(pid, position)
        if len(self.sup_dict) > 0:
            l.append(MenuItem('Support', self.support))

        self.exc = map.have_exchange_object(pid, position)
        if len(self.exc) > 0:
            l.append(MenuItem('Exchange', self.exchange))

        self.stl = map.can_steal(pid, position)
        if len(self.stl) > 0:
            l.append(MenuItem('Steal', self.steal, self.stl))

        doors, key = map.unlock_door(position, pid)
        if len(doors) > 0:
            l.append(MenuItem('Doors', self.doors, doors, key))

        talk_dict = map.find_talk_obj(pid, position)
        if len(talk_dict) > 0:
            l.append(MenuItem('Talk', self.talk, talk_dict))

        event = map.get_grid_event(position, pid)
        _type = event[0]
        if (_type is 'V') and (not event[1] is None):
            l.append(MenuItem('Visit', self.visitvillage, event[1]))
        elif _type is 'T'and (not event[1] is None):
            _event, _item = event[1], event[2]
            if _event is not None:
                l.append(MenuItem('Treasury', self.treasury, _event, _item))
        seize = map.get_seize_event(pid, position)
        if seize is not None:
            l.append(MenuItem('Seize', self.seize, seize))

        self.allow_cancel = arena.allow_cancel
        if self.allow_cancel:
            l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def on_mouse_release(self, x, y, buttons, modifiers):
        if buttons == 1:
            super().on_mouse_release(x, y, buttons, modifiers)

    def move(self):
        self.arena.move()
        self.parent.remove(self)

    def cancel(self):
        self.arena.cancel()
        self.parent.remove(self)

    def attack(self):
        self.arena.attack()
        self.parent.remove(self)

    def wand(self):
        self.arena.wand(self.avl)
        self.parent.remove(self)

    def support(self):
        self.arena.support(self.sup_dict)
        self.parent.remove(self)

    def item(self):
        self.arena.item_show()
        self.parent.remove(self)

    def exchange(self):
        self.arena.exchange(self.exc)
        self.parent.remove(self)

    def visitvillage(self, event):
        self.arena.visit_village(event)
        self.parent.remove(self)

    def treasury(self, event, item):
        self.arena.treasury(event, item)
        self.parent.remove(self)

    def seize(self, event):
        self.arena.seize(event)
        self.parent.remove(self)

    def steal(self, stl):
        self.arena.steal(stl)
        self.parent.remove(self)

    def doors(self, doors, key):
        self.arena.doors(doors, key)
        self.parent.remove(self)

    def talk(self, talk_dict):
        self.arena.talk(talk_dict)
        self.parent.remove(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4 :
            if self.allow_cancel:
                self.cancel()
            else:
                self.move()

class Showwand(Menu):
    is_event_handler = True

    def __init__(self, avl, arena):
        super().__init__(title='Wands')
        l = []
        for item in avl:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.wanduse, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.arena = arena

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def wanduse(self, item):
        self.parent.remove(self)
        self.arena.wanduse(item)

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(Ordermenu(self.arena))
        self.parent.remove(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Showweapon(Menu):
    is_event_handler = True

    def __init__(self, items, arena):
        super(Showweapon, self).__init__(title='Weapons')
        l = []
        for item in items:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.itemuse, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.arena = arena

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def itemuse(self, item):
        self.parent.remove(self)
        self.parent.add(Itemuse(item, self, self.arena))

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(Ordermenu(self.arena))
        self.parent.remove(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Itemuse(Menu):
    is_event_handler = True

    def __init__(self, item, menu, arena):
        super().__init__(title='Weapons')
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
        self.item = item
        self.menu = menu
        self.arena = arena

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

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
            if map.can_equip(arena.selected, item):
                l.append(MenuItem(item.itemtype.name, self.iteminfo, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.info = None
        self.arena = arena

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

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
        info.display(content)
        self.parent.remove(self)
        self.parent.disapper()
        self.arena.select_target(item, info)

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.arena.add_menu(Ordermenu(self.arena))
        self.parent.remove(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Exchangeitem(MenuItem):


    def on_activated(self):
        for obj in self.parent.get_children():
            try:
                obj.inactivate()
            except:
                pass
        self.item.color = (50, 250, 50, 200)

    def inactivate(self):
        self.item.color = (192, 192, 192, 255)


class Weaponexchange(Menu):
    is_event_handler = True
    selected = None
    def __init__(self, items, arena, position):
        super(Weaponexchange, self).__init__()
        l = []
        i = 0
        for i, item in enumerate(items):
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(Exchangeitem(content, self.item, i))
        if len(l) < 5:
            l.append(Exchangeitem('Empty', self.item, i+1))
        self.create_menu(l,None, None)
        self.position = position
        self.arena = arena
        self.selected = None

    def on_enter(self):
        super().on_enter()
        if self.parent.position == (0, 0):
            x, y = self.position
            self.position = (x + director.get_window_size()[0] * 3//4, y)

    def item(self, item):
        if self.selected is not None:
            for name in self.parent.children_names:
                if self.parent.children_names[name] == self:
                    self.name = name
            self.parent.remove('left')
            self.parent.remove('right')
            self.do(Delay(0.5) + CallFunc(self.arena.exchange_item(self.selected, item, self.name)))

        else:
            self.selected = item
            left = self.parent.get('left').selected
            right = self.parent.get('right').selected
            if left is not None and right is not None:
                self.parent.remove('left')
                self.parent.remove('right')
                self.do(Delay(0.5) + CallFunc(self.arena.exchange_item(left, right)))

    def cancel(self):
        self.arena.state = 'valid_dst'
        self.parent.add(Ordermenu(self.arena))
        self.parent.remove('left')
        self.parent.remove('right')

    def on_mouse_press(self, x, y, buttons, modifiers):
        left = self.parent.get('left')
        right = self.parent.get('right')
        if buttons == 4:
            if left.selected:
                self.do(Delay(0.5) + CallFunc(left.inactivate))
            elif right.selected:
                self.do(Delay(0.5) + CallFunc(right.inactivate))
            else:
                self.cancel()

    def inactivate(self):
        for obj in self.get_children():
            obj.inactivate()
        self.selected = None

class Setting(Menu):
    is_event_handler = True
    def __init__(self, arena):
        super().__init__(title='Settings')
        l = []
        l.append(MenuItem('Rolling', self.rolling))
        l.append(MenuItem('Moving', self.moving))
        l.append(MenuItem('Simplified', self.simple))
        l.append(MenuItem('Autoend', self.auto_end))
        l.append(MenuItem('Cancel', self.cancel))
        self.arena = arena

        self.create_menu(l, zoom_in(), zoom_out())


    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def rolling(self):
        self.parent.remove(self)
        self.parent.add(Fivelevelspeed(klass='rolling', arena=self.arena))

    def moving(self):
        self.parent.remove(self)
        self.parent.add(Fivelevelspeed(klass='moving', arena=self.arena))
        pass

    def simple(self):
        pass

    def cancel(self):
        self.parent.remove(self)
        self.parent.add(Endturn(self.arena))

    def auto_end(self):
        self.parent.remove(self)
        self.parent.add(Onoff(klass='endturn_automatically', arena=self.arena))

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Fivelevelspeed(Menu):
    is_event_handler = True
    def __init__(self, klass, arena):
        super().__init__(title=klass)
        l = []
        l.append(Exchangeitem('Very slow', self.adjust, 0))
        l.append(Exchangeitem('Slow', self.adjust, 1))
        l.append(Exchangeitem('Medium', self.adjust, 2))
        l.append(Exchangeitem('Fast', self.adjust, 3))
        l.append(Exchangeitem('Very fast', self.adjust, 4))
        l.append(MenuItem('Cancel', self.cancel))
        self.arena = arena
        self.klass = klass
        self.create_menu(l, None, None)
        l[arena.settings[klass]].item.color = (50, 250, 50, 200)
        pass


    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def adjust(self, level=0):
        dic = self.arena.settings
        dic[self.klass] = level
        self.arena.settings = dic
        self.parent.remove(self)
        self.parent.add(Setting(self.arena))

    def cancel(self):
        self.parent.remove(self)
        self.parent.add(Setting(self.arena))

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Onoff(Menu):
    def __init__(self, klass, arena):
        super().__init__(title=klass)
        l = []
        l.append(Exchangeitem('On', self.adjust, True))
        l.append(Exchangeitem('Off', self.adjust, False))
        self.arena = arena
        self.klass = klass
        self.create_menu(l, None, None)
        l[arena.settings[klass]].item.color = (50, 250, 50, 200)

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def adjust(self, level=0):
        dic = self.arena.settings
        dic[self.klass] = level
        self.arena.settings = dic
        self.parent.remove(self)
        self.parent.add(Setting(self.arena))

    def cancel(self):
        self.parent.remove(self)
        self.parent.add(Setting(self.arena))

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Endturn(Menu):
    is_event_handler = True
    def __init__(self, arena):
        super().__init__(title='Endturn')
        l = []
        l.append(MenuItem('Endturn', self.end_turn))
        l.append(MenuItem('Flags', self.flag))
        l.append(MenuItem('Save', self.save))
        l.append(MenuItem('Load', self.load))
        l.append(MenuItem('Cancel', self.cancel))
        l.append(MenuItem('Quit', self.quit))
        l.append(MenuItem('Jump', self.jump))
        l.append(MenuItem('Settings', self.setting))
        l.append(MenuItem('ShowAttackRange', self.showattrng))
        l.append(MenuItem('ShowThumb', self.showthumb))
        l.append(MenuItem('Status', self.status))
        self.create_menu(l, zoom_in(), zoom_out())
        self.arena = arena

    def on_enter(self):
        super().on_enter()
        x = self.parent.menu_back.position[0]
        self.position = x - director.get_window_size()[0] * 3 // 8, 0

    def cancel(self):
        director.window.push_handlers(self.arena)
        self.arena.state = 'default'
        self.parent.remove(self)
        self.parent.disapper()

    def flag(self):
        self.arena.flag()
        self.parent.remove(self)

    def save(self):
        self.arena.save()
        self.parent.remove(self)

    def load(self):
        self.arena.load()
        self.parent.remove(self)

    def end_turn(self):
        self.arena.end_turn()
        self.parent.remove(self)

    def jump(self):
        self.arena.jump()
        self.parent.remove(self)

    def showattrng(self):
        self.arena.showattrng()
        self.parent.remove(self)

    def showthumb(self):
        self.arena.showthumb()
        self.parent.remove(self)

    def status(self):
        self.arena.status()
        self.parent.remove(self)

    def quit(self):
        self.parent.remove(self)
        director.pop()

    def setting(self):
        self.parent.remove(self)
        self.parent.add(Setting(self.arena))

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Listwand(Menu):
    is_event_handler = True

    def __init__(self, items, arena, type):
        super().__init__(title='Wands')
        l = []
        for item in items:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            if type is 2:
                l.append(MenuItem(content, self.wandrpr, item))
            elif type is 3:
                l.append(MenuItem(content, self.wandstl, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.arena = arena
        self.type = type

    def wandrpr(self, item):
        self.parent.remove(self)
        self.arena.wandrpr(item)

    def wandstl(self, item):
        self.parent.remove(self)
        self.arena.wandstl(item)

    def cancel(self):
        self.parent.remove(self)
        avl = self.arena.map.available_wand(self.arena.selected)
        self.arena.wand(avl)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()

class Listcls(Menu):
    is_event_handler = True

    def __init__(self, cls_list, callback, **kwargs):
        super().__init__(title='CHOOSE PROMOTE')
        l = []
        for cls in cls_list:
            l.append(MenuItem(cls, self.promote, cls))
        self.create_menu(l, zoom_in(), zoom_out())
        self.callback = callback
        self.kwargs = kwargs

    def promote(self, cls):
        self.kill()
        self.callback.__call__(cls, **self.kwargs)
        del self




class Liststeal(Menu):
    is_event_handler = True
    def __init__(self, arena, steallist, callback, **kwargs):
        super().__init__(title='CHOOSE STEAL')
        l = []
        for item in steallist:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.steal, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.callback = callback
        self.kwargs = kwargs
        self.arena = arena

    def steal(self, item):
        self.kill()
        self.callback.__call__(item, **self.kwargs)
        del self

    def cancel(self):
        self.arena.cancel_select()
        self.parent.remove(self)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons == 4:
            self.cancel()
