from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QGraphicsItem
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

        self.scene = QGraphicsScene()
        self.scene.addText('Hello workd')
        self.setScene(self.scene)
        self.palette = QPalette()
        self.palette.setColor(self.backgroundRole(), BLACK)  # 设置背景颜色
        # palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('../../../Document/images/17_big.jpg')))   # 设置背景图片
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('3X_Qt')
        self.show()
        self.select = (-1, -1)
        self.on_mouse = (-1, -1)
        self.setMouseTracking(True)
        self.size = 80
        data = Data()
        global_vars = Global(data)
        terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
        person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
        self.map = map_controller.Main(terrain_container_test, person_container_test, global_vars)
        self.w = terrain_container_test.M
        self.h = terrain_container_test.N
        self.select = (-1, -1)
        for i in range(self.w):
            for j in range(self.h):
                x, y = i * self.size, j * self.size
                ec = self.scene.addEllipse(x, y, self.size, self.size, QPen(WHITE), QBrush(WHITE))
        position = self.map.person_container.position
        controller = self.map.person_container.controller

        self.person = {}
        for id in position:
            (i, j) = position[id]
            x, y = i * self.size, j * self.size
            if controller[id] == 1:
                self.scene.addEllipse(x, y, self.size, self.size, QPen(SKY_BLUE), QBrush(SKY_BLUE))
            else:
                self.scene.addEllipse(x, y, self.size, self.size, QPen(ORANGE), QBrush(ORANGE))

        self.ad = ec
        self.setMouseTracking(True)


    def mouseMoveEvent(self, QMouseEvent):
        x, y = QMouseEvent.x(), QMouseEvent.y()
        i, j = x // self.size, y // self.size
        if (i, j) != self.select:
            self.select = (i, j)
            self.scene.removeItem(self.ad)
            self.ad = self.scene.addEllipse(i * self.size, j * self.size, self.size, self.size,
                                  QPen(LIGHT_PINK), QBrush(LIGHT_PINK))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Arena()
    w.show()

    sys.exit(app.exec_())