# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/1 12:27
'''
from cocos.text import RichLabel


class Text(RichLabel):

    def __init__(self, **kwargs):
        super(Text, self).__init__(anchor_x='center',anchor_y='center', **kwargs)

def layout(content, pos_range=None, color=(127, 255, 170, 255),
           font_name='times new roman',font_size=36):
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
    for i, text in enumerate(reversed(content)):
        pos_y = (i + 1) / num * y_range + y0
        textlist.append(Text(text=text, position=(pos_x, pos_y), color=color,
                             font_size=font_size, font_name=font_name))
    return textlist


    pass

def layout_multiply(content, row, column, pos_range=None, color=(127, 255, 170, 255),
                    font_name='times new roman', font_size=36):

    if len(content) == 0:
        return []
    if pos_range is None:
        from cocos.director import director
        (x1, y1) = director.get_window_size()
        (x0, y0) = (0, 0)
    else:
        (x0, y0), (x1, y1) = pos_range

    _step = (x1 - x0) // (column + 1)
    _pos_range = (x0, y0), (x0 + _step, y1)
    _content = []
    textmap = []
    for i, text in enumerate(content):
        _content.append(text)
        if i % row == row - 1:
            _column = (i + 1) // row
            textmap.append(layout(_content, _pos_range, color, font_name, font_size))
            _content = []
            _pos_range = (x0 + _step * _column, y0), (x0 + _step * (_column + 1), y1)



    while not i % row == row - 1:
        i += 1
        _content.append(' ')

    _column = (i + 1) // row
    _pos_range = (x0, y0), (x0 + _step * (_column + 1), y1)
    textmap.append(layout(_content, _pos_range, color, font_name, font_size))
    return textmap