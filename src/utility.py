from PyQt5.QtGui import QColor
def coordinate(i, j, size):
    x = i * size + size // 2
    y = j * size + size // 2
    return x, y

def coordinate_t(x, y, size):
    i = x // size
    j = y // size
    return i, j

WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
LIGHT_PINK = QColor(255, 182, 193)
STEEL_BLUE = QColor(70, 130, 180)
CRIMSON = QColor(220, 20, 60)
VIOLET = QColor(238, 130, 238)
SLATEBLUE = QColor(106, 90, 205)
CYAN = QColor(0, 255, 255)
AUQAMARIN = QColor(127, 255, 170)
LIME = QColor(0, 255, 0)
YELLOW = QColor(255, 255, 0)
OLIVE = QColor(128, 128, 0)
CORNISLK = QColor(255, 248, 220)
ORANGE = QColor(255, 165, 0)
CORAL = QColor(255, 127, 80)
SKY_BLUE = QColor(135, 206, 235)
GOLD = QColor(255, 215, 0)
MAROON = QColor(128, 0, 0)