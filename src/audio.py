# coding=utf-8
'''
@author: Antastsy
@time: 2018/1/31 23:30
'''
import os
from cocos.layer import Layer
from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer

class Audiolayer(Layer):
    def __init__(self):
        mixer.init()
        super(Audiolayer, self).__init__()
        self.path = os.getcwd()
        os.chdir(self.path[0:-4])
        self.sound = Sound('audio/test.ogg')
        self.sound.play(-1)

    def on_exit(self):
        os.chdir(self.path)
        mixer.pause()

    def on_enter(self):
        mixer.unpause()
