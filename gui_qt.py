import sys
import re

from tkinter import *
from PyQt4.QtCore import Qt, QTimeLine, QPointF, SIGNAL, QEvent
from PyQt4.QtGui import (QMainWindow, QApplication, QMessageBox,
                         QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPixmap, QGraphicsItemAnimation, QCursor)
from PyQt4 import uic

from server import Server
import jsonSocket


class MyWin(QMainWindow):
    def __init__(self, address='127.0.0.1', port=5007):
        QMainWindow.__init__(self)
        uic.loadUi('untitled.ui', self)

        self.s = Server(address, port)
        self.s.start()
        self.is_client_connected = False

        self.view_config()
        self.scene = QGraphicsScene()
        self.my_screen.setScene(self.scene)
        self.scene1 = QGraphicsScene()
        self.enemys_screen.setScene(self.scene1)

        # self.my_screen.viewport().installEventFilter(self)

        self.generate_fields()

        # buttons
        self.shot_btn.clicked.connect(self.execute_shot)
        self.set_ship_btn.clicked.connect(self.set_ship)
        self.connect_btn.clicked.connect(self.connect_with_enemy)
        self.exit_btn.clicked.connect(self.close_app)
        pass

    def generate_fields(self):
        for i in range(5):
            for j in range(5):
                self.item = QGraphicsPixmapItem(QPixmap('hex1.gif'))
                if j % 2 == 0:
                        self.item.setOffset(i*110+55, j*70)
                else:
                    self.item.setOffset(i*110, j*70)
                self.scene.addItem(self.item)

        for i in range(5):
            for j in range(5):
                self.item = QGraphicsPixmapItem(QPixmap('hex1.gif'))
                if j % 2 == 0:
                    self.item.setOffset(i*110+55, j*70)
                else:
                    self.item.setOffset(i*110, j*70)
                self.scene1.addItem(self.item)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseMove and
                source is self.my_screen.viewport()):
                    QMessageBox.about(self, "Debug", "debug")

    def view_config(self):
        self.ip_addr_field.setPlaceholderText("Podaj adres IP przeciwnika")
        self.ip_addr_field.setAlignment(Qt.AlignCenter)

        self.set_X.setPlaceholderText("Podaj współżędną X statku")
        self.set_X.setAlignment(Qt.AlignCenter)

        self.set_Y.setPlaceholderText("Podaj współżędną Y statku")
        self.set_Y.setAlignment(Qt.AlignCenter)

        self.x_field.setPlaceholderText("Podaj współżędną X statku")
        self.x_field.setAlignment(Qt.AlignCenter)

        self.y_field.setPlaceholderText("Podaj współżędną Y statku")
        self.y_field.setAlignment(Qt.AlignCenter)

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
                    self.item = QGraphicsPixmapItem(QPixmap('hex2.gif'))
                    if y % 2 == 0:
                        self.item.setOffset(x*110+55, y*70)
                    else:
                        self.item.setOffset(x*110, y*70)
                    self.scene.addItem(self.item)
                elif x % 2 == 0:
                    self.item = QGraphicsPixmapItem(QPixmap('hex2.gif'))
                    if y % 2 == 0:
                        self.item.setOffset(x*110+55, y*70)
                    else:
                        self.item.setOffset(x*110, y*70)
                    self.scene.addItem(self.item)

                # self.client.sendObj({"x": x, "y": y})
            else:
                QMessageBox.about(self, "Błąd", "Niepoprawne pola")
        else:
            QMessageBox.about(self, "Info", "Nie połączyłeś się z przeciwnikiem")

    def set_ship(self):
        if not self.is_client_connected:
            x = self.set_X.text()
            y = self.set_Y.text()
            x, y = MyWin._parser(x, y)
            if x != -1 and y != -1:
                QMessageBox.about(self, "Statek na polu", "({}, {})".format(x, y))
                if x % 2 != 0:
                    # x -= 1;
                    if x == 1:
                        x -= 1
                    if x == 3:
                        x -= 2
                    self.item = QGraphicsPixmapItem(QPixmap('boat.gif'))
                    self.item.setOffset(10+y*110, 80+x*140)
                    self.scene.addItem(self.item)
                elif x % 2 == 0:
                    if x == 2:
                        x -= 1
                    if x == 4:
                        x -= 2
                    self.item = QGraphicsPixmapItem(QPixmap('boat.gif'))
                    self.item.setOffset(65+y*110, 20+x*140)
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

