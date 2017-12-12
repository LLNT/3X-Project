from PyQt5.QtWidgets import (QWidget, QToolTip,
    QPushButton, QApplication, QMessageBox)
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, Qt
import sys
import PyQt5
from global_vars import Main as Global
from data_loader import Main as Data
from terrain_container import Main as Terrain_Container
from person_container import Main as Person_Container
import map_controller
from utility import coordinate, coordinate_t
BLUE = QColor(70, 130, 180)
WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
PINK = QColor(255, 182, 193)

class Arena(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(self.backgroundRole(), BLACK)  # 设置背景颜色
        # palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('../../../Document/images/17_big.jpg')))   # 设置背景图片
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('3X_Qt')
        data = Data()
        global_vars = Global(data)
        terrain_container_test = Terrain_Container(data.terrain_map, global_vars.terrainBank)
        person_container_test = Person_Container(data.map_armylist, global_vars.personBank)
        map1 = map_controller.Main(terrain_container_test, person_container_test, global_vars)
        self.w = terrain_container_test.M
        self.h = terrain_container_test.N
        self.size = 80
        self.show()
        self.select = (-1, -1)
        self.on_mouse = (-1, -1)
        self.setMouseTracking(True)

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i in range(self.w):
            for j in range(self.h):
                x, y = i * self.size, j * self.size
                if (i, j) != self.select:
                    painter.setBrush(WHITE)
                else:
                    painter.setBrush(PINK)
                painter.drawEllipse(x, y, self.size, self.size)

        painter.end()
        self.painter = QPainter()
        self.painter.begin(self)



    def closeEvent(self, event):
        pass
        '''reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()'''



    def mouseMoveEvent(self, QMouseEvent):

        x, y = QMouseEvent.x(), QMouseEvent.y()
        i, j = x // self.size, y // self.size
        if (i, j) != self.select:
            self.select = (i, j)
            self.repaint()


    def grabMouse(self, QCursor=None):
        print(1)

    def mousePressEvent(self, QMouseEvent):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Arena()
    w.show()

    sys.exit(app.exec_())