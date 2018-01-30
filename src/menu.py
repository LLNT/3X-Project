# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/30 20:10
'''
from cocos.menu import Menu, MenuItem, zoom_in, zoom_out


class Optionmenu(Menu):
    is_event_handler = True
    def __init__(self, person, dst):
        super(Optionmenu, self).__init__(title='options')
        l = []
        l.append(MenuItem('Confirm', self.confirm))
        l.append(MenuItem('Cancel', self.cancel))
        self.create_menu(l, zoom_in(), zoom_out())
        self.person = person
        self.dst = dst


    def confirm(self):
        self.parent.confirm(self.person, self.dst)
        self.parent.remove(self)

    def cancel(self):
        self.parent.clear_map()
        self.parent.remove(self)

