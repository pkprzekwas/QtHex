import sys
import re

from tkinter import *
import numpy as np
from PyQt4.QtCore import Qt, QTimeLine, QPointF, SIGNAL, QEvent
from PyQt4 import uic
from PyQt4.QtGui import (QMainWindow, QApplication, QMessageBox,
                         QGraphicsScene, QGraphicsPixmapItem, QPixmap,)

from server import Server
from commons import parser
from draw_map import DrawMap
import jsonSocket


class MyWin(QMainWindow):
    def __init__(self, address='127.0.0.1', port=5007):
        QMainWindow.__init__(self)
        uic.loadUi('untitled.ui', self)

        self.my_board = np.zeros((9, 9))
        self.enemies_board = np.zeros((9, 9))

        self.my_points = 0
        self.enemies_points = 0

        self.my_ships = 0

        self.s = Server(address, port)
        self.s.start()
        self.is_client_connected = False

        self.view_config()
        self.scene = QGraphicsScene()
        self.my_screen.setScene(self.scene)
        self.scene1 = QGraphicsScene()
        self.enemys_screen.setScene(self.scene1)
        DrawMap(self.scene, self.scene1)

        # self.my_screen.viewport().installEventFilter(self)

        # buttons
        self.shot_btn.clicked.connect(self.execute_shot)
        self.set_ship_btn.clicked.connect(self.set_ship)
        self.connect_btn.clicked.connect(self.connect_with_enemy)
        self.exit_btn.clicked.connect(self.close_app)
        pass

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseMove and
                source is self.my_screen.viewport()):
                    QMessageBox.about(self, "Debug", "debug")

    def view_config(self):
        self.setWindowTitle(self.tr("Statki"))

        self.ip_addr_field.setPlaceholderText("Podaj adres IP przeciwnika")
        self.ip_addr_field.setAlignment(Qt.AlignCenter)

        self.set_X.setPlaceholderText("Podaj wspolzedna X statku")
        self.set_X.setAlignment(Qt.AlignCenter)

        self.set_Y.setPlaceholderText("Podaj wspolzedna Y statku")
        self.set_Y.setAlignment(Qt.AlignCenter)

        self.x_field.setPlaceholderText("Podaj wspolzedna X statku")
        self.x_field.setAlignment(Qt.AlignCenter)

        self.y_field.setPlaceholderText("Podaj wspolzedna Y statku")
        self.y_field.setAlignment(Qt.AlignCenter)

    def connect_with_enemy(self):
        ip_addr = self.ip_addr_field.text()
        pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        test = pattern.match(ip_addr)
        if test:
            QMessageBox.about(self, "Info", "{}".format(ip_addr))
            self.client = jsonSocket.JsonClient(address=ip_addr, port=5008)
            self.client.connect()
        else:
            QMessageBox.about(self, "Blad", "Bledny format adresu ip")

    def execute_shot(self):

        isHit = False

        if not self.is_client_connected:
            x = self.x_field.text()
            y = self.y_field.text()
            x, y = parser(x, y)
            if x != -1 and y != -1:

                if self.enemies_board[x][y] == 1:
                    self.enemies_board[x][y] = 2
                    isHit = True
                    QMessageBox.about(self, "Strzal", "Trafiony!!!")

                QMessageBox.about(self, "Strzal", "({}, {})".format(x, y))

                if x % 2 != 0:
                    self.item = QGraphicsPixmapItem(QPixmap('res/hex2.gif'))
                    if y % 2 == 0:
                        self.item.setOffset(x*110+55, y*70)
                    else:
                        self.item.setOffset(x*110, y*70)
                    self.scene1.addItem(self.item)
                elif x % 2 == 0:
                    self.item = QGraphicsPixmapItem(QPixmap('res/hex2.gif'))
                    if y % 2 == 0:
                        self.item.setOffset(x*110+55, y*70)
                    else:
                        self.item.setOffset(x*110, y*70)
                    self.scene1.addItem(self.item)

                # self.client.sendObj({"x": x, "y": y})
            else:
                QMessageBox.about(self, "Blad", "Niepoprawne pola")
        else:
            QMessageBox.about(self, "Info", "Nie polaczyles sie z przeciwnikiem")

    def set_ship(self):
        if not self.is_client_connected:
            x = self.set_X.text()
            y = self.set_Y.text()
            x, y = parser(x, y)

            if self.my_ships < 6:
                if x != -1 and y != -1:

                    # Dodanie statku do pola
                    self.my_board[x][y] = 1
                    self.my_ships += 1

                    QMessageBox.about(self, "Statek na polu", "({}, {})".format(x, y))
                    if x % 2 != 0:
                        self.item = QGraphicsPixmapItem(QPixmap('res/boat.gif'))
                        self.item.setOffset(3+y*61, 11+(x*52))
                        self.scene.addItem(self.item)
                    elif x % 2 == 0:
                        self.item = QGraphicsPixmapItem(QPixmap('res/boat.gif'))
                        self.item.setOffset(30+y*61, 0+x*53)
                        self.scene.addItem(self.item)
                    # self.client.sendObj({"x": x, "y": y})

                else:
                    QMessageBox.about(self, "Blad", "Niepoprawne pola")
            else:
                    QMessageBox.about(self, "Blad", "Wykorzystales juz cala flote")
        else:
            QMessageBox.about(self, "Info", "Nie polaczyles sie z przeciwnikiem")

    def close_app(self):
        if self.is_client_connected:
            self.client.close()
        self.s.stop()
        self.close()


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    mw = MyWin()
    mw.show()

    sys.exit(qApp.exec_())

