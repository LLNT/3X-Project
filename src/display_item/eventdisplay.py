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
from cocos.actions import CallFunc, Delay

class Eventdisplay(Layer):

    def __init__(self, event, map, dialog_type, dialog_info, w=640, h=480,
                 callback=None, **kwargs):
        super().__init__()
        self.map = map #type:map_controller.Main

        self.dialog_info = dialog_info
        self.dialog_type = dialog_type
        self.w, self.h = w, h
        self.callback = callback
        self.kwargs = kwargs
        self.event = event
        # get first condition_satisfied

    def display(self):
        self.map.global_vars.flags[self.event['Event']] = True
        if 'Text' in self.event.keys() and len(self.event['Text']) > 0:
            text_list = self.event['Text']
            text_source = self.map.global_vars.data.text
            if self.dialog_type is 'B':
                self.add(Battledialog(text_list, text_source, self.w, self.h,
                                      dialog_info=self.dialog_info, callback=self.get_finish))
            elif self.dialog_type is 'S':
                scene = Dialogscene(text_list, text_source, self.map, self.w, self.h,
                                                callback=self.get_finish, info=self.dialog_info)
                director.push(Scene(scene))
                scene.excute()

            elif self.dialog_type is 'M':
                self.add(Mapdialog(text_list, text_source, self.w, self.h, self.map, self.get_finish))
            else:
                self.get_finish()
        else:
            self.get_finish()

    def get_finish(self):
        self.finish = self.event['Finish']
        self.execute_finish = self.finish[-1]
        self.execute_event = self.finish[-1]['Execute']
        for item in self.finish:
            cd = item['Condition']
            if check_condition(cd, self.map):
                self.execute_event = item['Execute']
                self.execute_finish = item
                break
        self.length = len(self.execute_event)
        self.execute()

    def execute(self, i=0):
        if i < self.length:
            event = self.execute_event[i]
            _event = event.split('/')
            _type = _event[0]
            if _type == 'CLV':
                self.map.eventlist['Villages'].pop(_event[1])
                self.execute(i+1)
            elif _type == 'I':
                _, _itemid, _pid = _event
                if _pid == 'E':
                    _pid = self.dialog_info['E']
                if _pid == 'V':
                    _pid = self.dialog_info['V'].pid
                item = self.map.global_vars.itemBank[int(_itemid)]
                person = self.map.global_vars.personBank[_pid]
                flag = self.map.global_vars.flags['Have Transporter']
                git = Getitem(person, item, flag, self.map, callback=self.execute, i=i+1)
                self.add(git)
            elif _type == 'SF':
                flag = _event[1]
                self.map.global_vars.flags[flag] = True
                self.execute(i+1)
            elif _type == 'R':
                if 'Reinforce' not in self.kwargs:
                    self.kwargs['Reinforce'] = []
                self.kwargs['Reinforce'].append(_event)
                self.execute(i+1)
            else:
                print('Unknown event %s' % _event)
                self.execute(i + 1)
            pass
        else:
            jump = self.execute_finish['Jump']
            if jump is 'F':
                self.callback.__call__(**self.kwargs)
            elif jump is 'L':
                self.parent.defeated()
            elif jump is 'W':
                self.parent.win()
            else:
                general = self.map.eventlist['General']
                event = None
                for item in general:
                    if jump == item['Event']:
                        event = item
                        break
                if event is not None:
                    if 'Reconstruct' in event.keys():
                        self.parent.reconstruct(event['Reconstruct'])
                    jump_event = Eventdisplay(
                        event=event, map=self.map, w=self.w, h=self.h,
                        dialog_type=self.dialog_type, dialog_info=self.dialog_info,
                        callback=self.callback, **self.kwargs
                    )
                    self.parent.add(jump_event)
                    jump_event.display()
                else:
                    print('Jump Event %s not found' % jump)
                    self.callback.__call__(**self.kwargs)
            self.kill()
        pass

class Afterevent(Eventdisplay):

    # here the event receives in init method is a list of events

    def display(self):
        self.i = 0
        text_list = self.event[self.i]['Text']
        text_source = self.map.global_vars.data.text
        tag = self.event[self.i]['Tag']
        self.event_length = len(self.event)
        self.keep = Afterdialog(text_list, text_source, self.map, self.w, self.h, tag=tag,
                                        callback=self._callback, info=self.dialog_info)
        self.scene = Layer()
        director.push(Scene(self.scene))
        self.scene.add(self.keep)
        self.keep.excute()

    def _callback(self, **kwargs):
        self.length = len(self.event[self.i]['Execute'])
        self.execute()

    def execute(self, i=0):
        if i < self.length:
            event = self.event[self.i]['Execute'][i]
            _event = event.split('/')
            _type = _event[0]
            if _type == 'CLV':
                self.map.eventlist['Villages'].pop(_event[1])
                self.execute(i+1)
            elif _type == 'I':
                _, _itemid, _pid = _event
                if _pid == 'E':
                    _pid = self.dialog_info['E']
                if _pid == 'V':
                    _pid = self.dialog_info['V'].pid
                item = self.map.global_vars.itemBank[int(_itemid)]
                person = self.map.global_vars.personBank[_pid]
                flag = self.map.global_vars.flags['Have Transporter']
                getitem = Getitem(person, item, flag, self.map,
                                 callback=self.execute, i=i+1)
                self.scene.add(getitem)
                director.window.remove_handlers(self)
            elif _type == 'SF':
                flag = _event[1]
                self.map.global_vars.flags[flag] = True
                self.execute(i+1)
            elif _type == 'R':
                if 'Reinforce' not in self.kwargs:
                    self.kwargs['Reinforce'] = []
                self.kwargs['Reinforce'].append(_event)
                self.execute(i+1)
            elif _type == 'MAP':
                self.kwargs['Map'] = _event[1]
                self.execute(i+1)
            else:
                print('Unknown event %s' % _event)
                self.execute(i + 1)
            pass
        else:
            print('next')
            self.get_next_event()

    def get_next_event(self):
        self.i += 1
        if self.i < self.event_length:
            event = self.event[self.i]
            text_list = event['Text']
            text_source = self.map.global_vars.data.text
            if len(text_list) > 0:
                if self.event[self.i-1]['Keep'] is 1:
                    scene = self.keep #type: Afterdialog
                    scene.textlist = text_list
                    scene.textsource = text_source
                    scene.length = len(text_list)
                    scene.i = 0
                    print('Keep')
                else:

                    scene = Afterdialog(text_list, text_source, self.map, self.w, self.h,
                                        callback=self._callback, info=self.dialog_info)
                self.scene.add(scene)
                self.keep = scene
                scene.excute()
            else:
                self._callback()
        else:
            director.pop()
            self.kill()
            self.callback.__call__(**self.kwargs)

if __name__ == '__main__':
    pass