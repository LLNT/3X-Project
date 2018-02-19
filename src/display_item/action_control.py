"""
@version: ??
@author: Antastsy
@time: 18-2-19 
"""

from cocos.actions import CallFunc, Action
from cocos.cocosnode import CocosNode

class Sequencial():
    def __init__(self, *args):
        '''

        :param args: list of tuple(object, action)
        '''
        self.length = len(args)
        self.actionlist = args

    def excute(self, i=0):
        if i < self.length:
            _object, _action = self.actionlist[i]  #type:CocosNode, Action
            _object.do(_action + CallFunc(self.excute, i+1))
        else:
            print('excuted')


