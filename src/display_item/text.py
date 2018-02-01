# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 12:27
'''
from cocos.text import RichLabel


class Text(RichLabel):

    def __init__(self, content, position, color=(127, 255, 170, 255),
                 font_name='times new roman',font_size=36):


        super(Text, self).__init__(text=content,
                                   font_name=font_name,
                                   font_size=font_size,
                                   position=position,
                                   color=color,
                                   anchor_x='center',
                                   anchor_y='center')

def layout(content, pos_range=None, color=(127, 255, 170, 255), font_name='times new roman',font_size=36):
    '''

    :param content: a list of text to be shown
    :param pos_range: two tuple of the shown range
    :return: a list of Text Object
    '''
    if pos_range is None:
        from cocos.director import director
        (x1, y1) = director.get_window_size()
        (x0, y0) = (0, 0)
    else:
        (x0, y0), (x1, y1) = pos_range
    num = len(content) + 1
    pos_x = (x0 + x1) / 2
    y_range = (y1 - y0)
    textlist = []
    for i, text in enumerate(content):
        pos_y = (i + 1) / num * y_range + y0
        textlist.append(Text(text, (pos_x, pos_y)))
    return textlist


    pass