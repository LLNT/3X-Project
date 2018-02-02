# coding=utf-8
'''
@author: Antastsy
@time: 2018/2/2 19:56
'''

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_PINK = (255, 182, 193)
STEEL_BLUE = (70, 130, 180)
CRIMSON = (220, 20, 60)
VIOLET = (238, 130, 238)
SLATEBLUE = (106, 90, 205)
CYAN = (0, 255, 255)
AUQAMARIN = (127, 255, 170)
LIME = (0, 255, 0)
YELLOW = (255, 255, 0)
OLIVE = (128, 128, 0)
CORNISLK = (255, 248, 220)
ORANGE = (255, 165, 0)
CORAL = (255, 127, 80)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)
MAROON = (128, 0, 0)
RED = (255, 0, 0)


mapstate2color = {
    'default': WHITE,
    'in_self_moverange': STEEL_BLUE,
    'in_enemy_moverange': CORAL,
    'in_ally_moverange': SLATEBLUE,
    'in_self_attackrange': LIME,
    'target': RED,
}

mapstate2color_motion = {
    'default': LIGHT_PINK,
    'in_self_moverange': VIOLET,
    'in_enemy_moverange': YELLOW,
    'in_ally_moverange': SLATEBLUE,
    'in_self_attackrange': GOLD,
    'target': RED,
}

self_state2color = {
    'unmoved': SKY_BLUE,
    'moved': OLIVE,
    'selected': VIOLET,
    'on_mouse_motion': VIOLET,
    'target': RED,
}

ally_state2color = {
    'unmoved': STEEL_BLUE,  # unmoved
    'moved': OLIVE,
    'selected': SKY_BLUE,
    'on_mouse_motion': VIOLET,
    'target': RED,
}

enemy_state2color = {
    'unmoved': ORANGE,  # unmoved
    'moved': OLIVE,
    'selected': GOLD,
    'on_mouse_motion': VIOLET,
    'target': RED,
}

ctrl2map_moverange = {
    0:'in_self_moverange',
    1:'in_enemy_moverange',
    2:'in_ally_moverange'
}

def per_state2color(state, ctrl):
    if ctrl == 0:
        return self_state2color[state]
    elif ctrl == 2:
        return ally_state2color[state]
    elif ctrl == 1:
        return enemy_state2color[state]
    else:
        return BLACK


if __name__ == '__main__':
    pass