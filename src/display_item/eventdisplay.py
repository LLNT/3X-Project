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
from utility import check_condition

class Eventdisplay(Layer):

    is_event_handler = True

    def __init__(self, event, map, dialog_type, dialog_info, w=640, h=480,
                 callback=None, **kwargs):
        super().__init__()
        self.map = map #type:map_controller.Main
        self.map.global_vars.flags[event['Event']] = True
        print(event)

        self.dialog_info = dialog_info
        self.w, self.h = w, h
        self.callback = callback
        self.kwargs = kwargs
        self.event = event
        try:
            text_list = event['Text']
            text_source = map.global_vars.text
        except:
            self.get_finish()
            return

        if dialog_type is 'B':
            self.add(Battledialog(text_list, text_source, w, h,
                                  dialog_info=dialog_info,callback=self.get_finish))
        elif dialog_type is 'S':
            director.push(Scene(Dialogscene(text_list, text_source, map, w, h,
                                            callback=self.get_finish, info=dialog_info)))
        elif dialog_type is 'M':
            self.add(Mapdialog(text_list, text_source, w, h, dialog_info, self.get_finish))
        else:
            self.get_finish()

    def get_finish(self):
        self.finish = self.event['Finish']
        # get first condition_satisfied
        self.execute_event = self.finish[-1]['Execute']
        for item in self.finish:
            cd = item['Condition']
            if check_condition(cd, self.map):
                self.execute_event = item['Execute']
                break

        self.length = len(self.execute_event)
        self.execute()

    def execute(self, i=0):
        if i < self.length:
            event = self.execute_event[i]
            _event = event.split('/')
            _type = _event[0]
            if _type is 'CLV':
                self.map.eventlist.pop(_event[1])
                self.execute(i+1)
            elif _type is 'I':
                _, _itemid, _pid = _event
                if _pid is 'E':
                    _pid = self.dialog_info['E']
                if _pid is 'V':
                    _pid = self.dialog_info['V'].pid
                item = self.map.global_vars.itemBank[int(_itemid)]
                person = self.map.global_vars.personBank[_pid]
                flag = self.map.global_vars.flags['Have Transporter']
                self.add(Getitem(person, item, flag, self.map, callback=self.execute, i=i+1))
            elif _type is 'SF':
                flag = _event[1]
                self.map.global_vars.flags[flag] = True
                self.execute(i+1)
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