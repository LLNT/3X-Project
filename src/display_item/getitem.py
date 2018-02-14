# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/14 22:23
'''
from cocos.layer import Layer
from cocos.menu import MenuItem, Menu, zoom_out, zoom_in
from cocos.director import director
from cocos.actions import Delay, CallFunc
from display_item.info import Info

class Getitem(Layer):
    is_event_handler = True
    def __init__(self, person, item, flag, map, maxitems=5):
        '''
        the layer to process getitem displaying.
        pass the pid; if the length of items<maxitem then just add normally
        else list all items include the new item, wait for events
        :param person:
        :param item: the item need to add
        :param flag: if transport allows
        :param maxitems:
        '''
        super().__init__()
        self.items = person.item

        # display the item just get first
        self.info = Info()
        self.add(self.info)
        self.info.display([item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)])
        self.item = item
        self.person = person
        self.maxitems = maxitems
        self.flag = flag
        self.map = map

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.person.item.append(self.item)
        director.window.remove_handlers(self)
        if len(self.items) <= self.maxitems:
            self.exit()
        else:
            self.info.kill()
            del self.info
            self.add(Listwand(self.items, self.flag))


    def exit(self):
        self.kill()
        self.parent.end_getitem()
        del self
        pass

class Listwand(Menu):
    is_event_handler = True
    def __init__(self, items, flag):
        super().__init__(title='Items')
        l = []
        for item in items:
            content = item.itemtype.name + ' ' + str(item.use) + '/' + str(item.itemtype.max_use)
            l.append(MenuItem(content, self.call_banish, item))
        self.create_menu(l, zoom_in(), zoom_out())
        self.flag = flag

    def call_banish(self, item):
        self.kill()
        director.window.remove_handlers(self)
        ba = Banish(item, self.flag)
        self.parent.do(Delay(0.2) + CallFunc(self.parent.add, ba))
        pass

class Banish(Menu):
    is_event_handler = True
    def __init__(self, item, flag):
        super().__init__(title='Handle')
        l = []
        l.append(MenuItem('Banish', self.banish, item))
        if flag:
            l.append(MenuItem('Transport', self.transport, item))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())

    def banish(self, item):
        self.kill()
        self.parent.person.banish(item)
        self.parent.exit()
        pass

    def transport(self, item):
        self.kill()
        self.parent.map.send_to_transporter(item)
        self.parent.exit()

    def cancel(self):
        self.kill()
        self.parent.add(Listwand(self.parent.items, self.parent.flag))

if __name__ == '__main__':
    pass