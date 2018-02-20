"""
@version: ??
@author: Antastsy
@time: 18-2-19 
"""

from cocos.actions import CallFunc, Action
from cocos.cocosnode import CocosNode
from typing import Set

class Sequencial():
    def __init__(self, *args):
        '''

        :param args: list of tuple(target, action)
        '''
        self.length = len(args)
        self.actionlist = args

    def excute(self, i=0):
        if i < self.length:
            _target, _action = self.actionlist[i]  #type:CocosNode, Action
            if _target is None:
                _target = CocosNode()
            _target.do(_action + CallFunc(self.excute, i+1))
        else:
            print('excuted')

class Graphic():
    def __init__(self, *args):
        '''

        :param args: list of target, action and set of preconditions id
        '''
        self.length = len(args)
        self.actionlist = args
        self.remains = set(range(self.length))

    def _done(self, i):
        if i in self.remains:
            self.remains.remove(i)
        if len(self.remains) == 0:
            print('excuted')
            return
        self.excute()

    def _excute(self, i):
        _target, _action, _ = self.actionlist[i]  # type:CocosNode, Action
        _target.do(_action + CallFunc(self._done, i))

    def excute(self, i=None):
        if i is not None:
            self._excute(i)
        else:
            for j in self.remains.copy():
                pres = self.actionlist[j][2]  # type:Set
                if pres & self.remains == set():
                    self._excute(j)