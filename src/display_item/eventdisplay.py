"""
@version: ??
@author: Antastsy
@time: 2018/2/22 2:52
"""
from cocos.layer import Layer
from cocos.scene import Scene
import map_controller
from display_item.dialog import *
from display_item.getitem import Getitem

class Eventdisplay(Layer):

    is_event_handler = True

    def __init__(self, event, map, dialog_type, left, right, w, h,
                 callback, **kwargs):
        super().__init__()
        self.map = map #type:map_controller.Main
        self.map.global_vars.flags[event['Event']] = True
        text_list = event['Text']
        text_source = map.global_vars.text
        self.left, self.right = left, right
        self.w, self.h = w, h
        self.callback = callback
        self.kwargs = kwargs

        self.finish = event['Finish']
        # get first condition_satisfied
        self.execute_event = self.finish[-1]['Execute']
        self.length = len(self.execute_event)

        if dialog_type is 'B':
            self.add(Battledialog(text_list, text_source, w, h, {},self.execute))
        elif dialog_type is 'S':
            director.push(Scene(Dialogscene(text_list, text_source, map, w, h, callback=self.execute, left=self.left)))


    def execute(self, i=0):
        if i < self.length:
            event = self.execute_event[i]
            _type = event.split('/')[0]
            if _type is 'CLV':
                self.map.eventlist.pop(event.split('/')[1])
                self.execute(i+1)
            elif _type is 'I':
                _, _itemid, _pid = event.split('/')
                item = self.map.global_vars.itemBank[int(_itemid)]
                person = self.map.global_vars.personBank[_pid]
                flag = self.map.global_vars.flags['Have Transporter']
                self.add(Getitem(person, item, flag, self.map, callback=self.execute, i=i+1))
            else:
                print('Unknown event type')
                self.execute(i+1)
            pass
        else:
            # add jump event here
            self.callback.__call__(**self.kwargs)
        pass


if __name__ == '__main__':
    pass