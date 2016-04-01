import sys
import re

from tkinter import *
from PyQt4.QtCore import Qt, QTimeLine, QPointF
from PyQt4.QtGui import (QMainWindow, QApplication, QMessageBox,
                         QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPixmap, QGraphicsItemAnimation)
from PyQt4 import uic


from server import Server
import jsonSocket


class MyWin(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('untitled.ui', self)

        self.s = Server()
        self.s.start()
        self.is_client_connected = False

        self.view_config()
        self.scene = QGraphicsScene()
        self.my_screen.setScene(self.scene)

        # item = QGraphicsRectItem(0, 0, 100, 50)
        # item = QGraphicsPixmapItem(QPixmap('Hexagon_1000.gif'))
        # self.scene.addItem(item)

        for i in range(5):
            for j in range(5):
                # self.item = QGraphicsRectItem(i*50, j*50, 10, 10)
                self.item = QGraphicsPixmapItem(QPixmap('hex2.gif'))
                if j % 2 == 0:
                    self.item.setOffset(i*110+55, j*70)
                else:
                    self.item.setOffset(i*110, j*70)
                self.scene.addItem(self.item)

        # self.item = QGraphicsRectItem(100+110, 45+140, 10, 10)
        # self.scene.addItem(self.item)
        #
        # self.item = QGraphicsRectItem(45+110, 110+0, 10, 10)
        # self.scene.addItem(self.item)
        #
        # self.item = QGraphicsRectItem(45+3*110, 110+0, 10, 10)
        # self.scene.addItem(self.item)
        #
        # self.item = QGraphicsRectItem(45+3*110, 110+140, 10, 10)
        # self.scene.addItem(self.item)

        # buttons
        self.shot_btn.clicked.connect(self.execute_shot)
        self.connect_btn.clicked.connect(self.connect_with_enemy)
        self.exit_btn.clicked.connect(self.close_app)
        pass

    def view_config(self):
        self.ip_addr_field.setPlaceholderText("Podaj adres IP przeciwnika")
        self.ip_addr_field.setAlignment(Qt.AlignCenter)

    def connect_with_enemy(self):
        ip_addr = self.ip_addr_field.text()
        pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        test = pattern.match(ip_addr)
        if test:
            QMessageBox.about(self, "Info", "{}".format(ip_addr))
            # self.client = jsonSocket.JsonClient(address=ip_addr, port=5007)
            # self.client.connect()
        else:
            QMessageBox.about(self, "Błąd", "Błędny format adresu ip")

    def execute_shot(self):
        if not self.is_client_connected:
            x = self.x_field.text()
            y = self.y_field.text()
            x, y = MyWin._parser(x, y)
            if x != -1 and y != -1:
                QMessageBox.about(self, "Strzał", "({}, {})".format(x, y))
                if x % 2 != 0:
                    x = x-1;
                    self.item = QGraphicsRectItem(45+y*110, 110+x*140, 12, 12)
                    self.scene.addItem(self.item)
                elif x % 2 == 0:
                    if x != 0:
                        x -= 1
                    self.item = QGraphicsRectItem(100+y*110, 45+x*140, 12, 12)
                    self.scene.addItem(self.item)
                # self.client.sendObj({"x": x, "y": y})
            else:
                QMessageBox.about(self, "Błąd", "Niepoprawne pola")
        else:
            QMessageBox.about(self, "Info", "Nie połączyłeś się z przeciwnikiem")

    def close_app(self):
        if self.is_client_connected:
            self.client.close()
        self.s.stop()
        self.close()

    @staticmethod
    def _parser(x, y):
        try:
            x = int(x)
            y = int(y)
            if x not in range(6):
                x, y = -1, -1
            if y not in range(6):
                x, y = -1, -1
        except ValueError:
            x, y = -1, -1
        return x, y


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    mw = MyWin()
    mw.show()

    sys.exit(qApp.exec_())

