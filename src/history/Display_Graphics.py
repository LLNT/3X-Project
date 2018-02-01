from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QGraphicsItem, QGraphicsEllipseItem, QGraphicsSceneMouseEvent

from PyQt5.Qt import QPropertyAnimation, QPoint
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import *
import sys
from utility import *
from global_vars import Main as Global
from data_loader import Main as Data
from terrain_container import Main as Terrain_Container
from person_container import Main as Person_Container
import map_controller
class Arena(QGraphicsView):
    def __init__(self, size=80):
        super(Arena, self).__init__()
        self.size = size
        self.set_beckground()
        self.set_datas()
        self.set_tiles()
        self.set_roles()
        self.setMouseTracking(True)

    def set_beckground(self):
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.palette = QPalette()
        self.palette.setColor(self.backgroundRole(), BLACK)  # 设置背景颜色
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)
        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle('3X_Qt')
        self.show()

    def set_datas(self):
        data = Data()
        global_vars = Global(data)
        terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
        person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
        self.map = map_controller.Main(terrain_container_test, person_container_test, global_vars)
        self.w = terrain_container_test.M
        self.h = terrain_container_test.N

    def set_tiles(self):
        self.select = (-1, -1)
        for i in range(self.w):
            for j in range(self.h):
                ec = self.add_tile(i, j, self.size, WHITE)
        self.ad = ec

    def set_roles(self):
        position = self.map.person_container.position
        controller = self.map.person_container.controller
        self.roles = []
        for id in position:
            (i, j) = position[id]
            if controller[id] == 1:
                self.roles.append(self.add_role(i, j, self.size, SKY_BLUE))
            else:
                self.roles.append(self.add_role(i, j, self.size, ORANGE))

    '''def mouseMoveEvent(self, QMouseEvent):
        x, y = QMouseEvent.x(), QMouseEvent.y()
        i, j = x // self.size, y // self.size
        if (i, j) != self.select:
            self.select = (i, j)
            self.scene.removeItem(self.ad)'''

    def add_role(self, i, j, size, color):
        tmp = Role(i *size, j * size, size, size)
        tmp.setBrush(QBrush(color))
        tmp.setPen(QPen(color))
        self.scene.addItem(tmp)
        return tmp

    def add_tile(self, i, j, size, color):
        tmp = Tile(i *size, j * size, size, size)
        tmp.setBrush(QBrush(color))
        tmp.setPen(QPen(color))
        self.scene.addItem(tmp)
        return tmp


class Role(QGraphicsEllipseItem):
    select = False


    def __init__(self, i, j, w, h):
        super(Role, self).__init__(i, j, w, h)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setAcceptDrops(True)

    '''def mousePressEvent(self, QGraphicsSceneMouseEvent):
        x, y = QGraphicsSceneMouseEvent.pos().x(), QGraphicsSceneMouseEvent.pos().y()
        i, j = x // 80, y // 80
        x ,y = x * 80, y * 80
        if not self.select:
            self.select = True
            print(self.pos())
        else:
            self.select = False
            animation = QPropertyAnimation(self, 'pos')
            animation.setDuration(1)
            animation.setStartValue(QPoint(self.pos()))
            animation.setEndValue(QPoint(300, 300))
            animation.start()'''
    def dragEnterEvent(self, QGraphicsSceneDragDropEvent):
        print(QGraphicsSceneDragDropEvent)
        QGraphicsSceneDragDropEvent.accept()

    def mouseMoveEvent(self, e):
        self.moveBy(e.pos().x(), e.pos().y())

    def mousePressEvent(self, e):

        if e.button() == Qt.LeftButton:
            print('press')


class Tile(QGraphicsEllipseItem):
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Arena()
    w.show()

    sys.exit(app.exec_())