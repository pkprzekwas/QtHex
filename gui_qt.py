import sys
import re

from tkinter import *
import numpy as np
import pickle
from random import randint
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from PyQt4.QtCore import Qt, QEvent
from PyQt4 import uic
from PyQt4.QtGui import (QMainWindow, QApplication, QMessageBox, QCursor,
                         QGraphicsScene, QGraphicsPixmapItem, QPixmap,
                         QAction, QIcon, QFileDialog)
from commons import parser
from ai import AI
from draw_map import DrawMap
from window_config import WindowConfig
from game_server import Server
import jsonSocket


class MyWin(QMainWindow):

    STATEK = 'res/ship1.png'

    def __init__(self, address='127.0.0.1', port=5007):
        QMainWindow.__init__(self)
        uic.loadUi('untitled.ui', self)

        self.step_nr = 0
        self.is_my_turn = True
        self.ai_mode = False

        #  List with game states
        self.state = []

        self.ready_to_play = False
        self.send = (-1, -1)

        # 1 - Ship
        # 2 - Hit
        # 3 - Missed 
        self.my_board = np.zeros((10, 9))
        self.enemies_board = np.zeros((10, 9))
        self.build_ships_from_matrix()
        self.tie = 0
        self.my_points = 0
        self.enemies_points = 0

        self.xml_init()
        self.state.append((self.my_board, self.enemies_board, self.my_points))

        self.my_ships = 0

        self.s = Server(self, address, port)
        self.s.start()

        self.is_client_connected = False

        WindowConfig.config(self)
        self.scene = QGraphicsScene()
        self.my_screen.setScene(self.scene)

        self.dm = DrawMap(self.scene)

        # self.my_screen.viewport().installEventFilter(self)

        # buttons

        self.ai_btn.clicked.connect(self.play_with_ai)
        self.move_btn.clicked.connect(self.move_ship)
        self.next_btn.clicked.connect(self.next_step)
        self.back_btn.clicked.connect(self.step_back)
        self.save_btn.clicked.connect(self.save_dialog)
        self.clear_btn.clicked.connect(self.clear_board)
        self.read_file_btn.clicked.connect(self.load_state)
        self.gen_rand_btn.clicked.connect(self.build_random_matrix)
        self.shot_btn.clicked.connect(self.execute_shot)
        self.set_ship_btn.clicked.connect(self.set_ship)
        self.connect_btn.clicked.connect(self.connect_with_enemy)
        self.exit_btn.clicked.connect(self.close_app)
        pass

    def xml_init(self):
        self.root = ET.Element("game")

        doc = ET.SubElement(self.root, "initialization")
        ET.SubElement(doc, "my_board", name="my board").text = str(self.my_board)
        ET.SubElement(doc, "enemies_board", name="enemies board").text = str(self.my_board)

    def play_with_ai(self):
        self.ai_mode = True
        self.ai = AI(self)
        pass

    def move_ship(self):
        x = self.x_field.text()
        y = self.y_field.text()
        x, y = parser(x, y)

        if (x != -1 and y != -1) and \
                (self.my_board[x][y] == 1):
            new_x = randint(0, 9)
            new_y = randint(0, 8)
            if self.my_board[new_x][new_y] not in range(1,4):
                self.my_board[x][y] = 0
                self.my_board[new_x][new_y] = 1
                self.clear_board()
                self.build_shots_from_matrix()
        else:
            QMessageBox.about(self, "Move", "Wybierz statek")
        pass

    def next_step(self):
        self.my_board = self.state[self.step_nr][0]
        self.enemies_board = self.state[self.step_nr][1]
        self.my_points = self.state[self.step_nr][2]

        self.clear_board()
        self.build_shots_from_matrix()
        self.step_nr += 1

    def step_back(self):
        self.step_nr -= 1

        self.my_board = self.state[self.step_nr][0]
        self.enemies_board = self.state[self.step_nr][1]
        self.my_points = self.state[self.step_nr][2]

        self.clear_board()
        self.build_shots_from_matrix()

    def save_dialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file',
                '/home')

        pickle.dump( self.state, open( fname, "wb" ) )

        self.tree = ET.ElementTree(self.root)

        xmlstr = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        with open("newState.xml", "w") as f:
            f.write(xmlstr)

        # self.tree.write("states.xml")

    def load_state(self):
        '''
        Reads game state from binary file.
        '''

        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.state = pickle.load(open(fname, "rb"))

        # TODO
        tree = ET.parse('New_Database.xml')
        root = tree.getroot()

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
                source is self.my_screen.viewport()):
                    QCursor.pos()
                    QMessageBox.about(self, "Debug", "debug {}".format(QCursor.pos()))

    def connect_with_enemy(self):
        '''
        Connects our game instance with our enemy
        '''
        ip_addr = self.ip_addr_field.text()
        port = self.port_field.text()
        port = int(port)

        pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        test = pattern.match(ip_addr)

        if test:
            QMessageBox.about(self, "Info", "{}".format(ip_addr, port))
            self.connect_btn.hide()
            self.ip_addr_field.hide()
            self.port_field.hide()
            self.client = jsonSocket.JsonClient(address=ip_addr, port=port)
            self.client.connect()
        else:
            QMessageBox.about(self, "Blad", "Bledny format adresu ip")

    def execute_shot(self):
        '''
        Shot execution.
        '''
        is_hit = False

        if not self.ai_mode:

            if not self.is_my_turn:
                QMessageBox.about(self, "Czekaj", "Czekaj na twoją turę!")
                return

            if not self.is_client_connected:
                x = self.x_field.text()
                y = self.y_field.text()
                x, y = parser(x, y)

                if x != -1 and y != -1:

                    if self.enemies_board[x][y] == 1:
                        self.enemies_board[x][y] = 2
                        is_hit = True
                        picture = 'res/ok.png'
                    else:
                        self.enemies_board[x][y] = 3
                        is_hit = False
                        picture = 'res/cancel.png'

                    # if x % 2 != 0:
                    #     self.item = QGraphicsPixmapItem(QPixmap(picture))
                    #     self.item.setOffset(16+y*61, 17+(x*52))
                    #     self.scene.addItem(self.item)
                    #
                    #
                    # elif x % 2 == 0:
                    #     self.item = QGraphicsPixmapItem(QPixmap(picture))
                    #     self.item.setOffset(47+y*61, 16+x*53)
                    #     self.scene.addItem(self.item)

                    # QMessageBox.about(self, "Strzal", "({}, {})".format(x, y))
                    self.send = (x, y)
                    self.client.sendObj({"x": x, "y": y})
                else:
                    QMessageBox.about(self, "Blad", "Niepoprawne pola")
            else:
                QMessageBox.about(self, "Info", "Nie polaczyles sie z przeciwnikiem")

            if is_hit:
                pass
            else:
                pass

        else:
            x = self.x_field.text()
            y = self.y_field.text()
            x, y = parser(x, y)

            if x != -1 and y != -1:

                if self.enemies_board[x][y] == 1:
                    self.enemies_board[x][y] = 2
                    is_hit = True
                    picture = 'res/ok.png'
                else:
                    self.enemies_board[x][y] = 3
                    is_hit = False
                    picture = 'res/cancel.png'

                self.is_my_turn = False
                self.ai.make_move()

    def get_shot(self, x, y):
        '''
        Shot handler.
        :param x: x coord of shot
        :param y: y coord of shot
        '''
        is_Hit = False

        if self.my_board[x][y] == 1:
            self.my_board[x][y] = 2
            is_hit = True
            picture = 'res/ok.png'
        else:
            self.my_board[x][y] = -1
            is_hit = False
            picture = 'res/cancel.png'

        if x % 2 != 0:
            self.item = QGraphicsPixmapItem(QPixmap(picture))
            self.item.setOffset(16+y*61, 17+(x*52))
            self.scene.addItem(self.item)

        elif x % 2 == 0:
            self.item = QGraphicsPixmapItem(QPixmap(picture))
            self.item.setOffset(47+y*61, 16+x*53)
            self.scene.addItem(self.item)

    def set_ship(self):
        if not self.is_client_connected:
            x = self.set_X.text()
            y = self.set_Y.text()
            x, y = parser(x, y)

            if self.my_ships < 10:
                if x != -1 and y != -1:

                    # Dodanie statku do pola
                    self.my_board[x][y] = 1
                    self.my_ships += 1

                    self.enemies_board[x][y] = 1

                    QMessageBox.about(self, "Statek na polu", "({}, {})".format(x, y))
                    if x % 2 != 0:
                        self.item = QGraphicsPixmapItem(QPixmap(self.STATEK))
                        self.item.setOffset(18+y*61, 21+(x*52))
                        self.scene.addItem(self.item)

                    elif x % 2 == 0:
                        self.item = QGraphicsPixmapItem(QPixmap(self.STATEK))
                        self.item.setOffset(49+y*61, 21+x*53)
                        self.scene.addItem(self.item)

                else:
                    QMessageBox.about(self, "Blad", "Niepoprawne pola")
            else:
                    QMessageBox.about(self, "Blad", "Wykorzystales juz cala flote")
        else:
            QMessageBox.about(self, "Info", "Nie polaczyles sie z przeciwnikiem")

        if self.my_ships == 5:
            self.ready_to_play = True
            self.set_X.hide()
            self.set_Y.hide()
            self.set_ship_btn.hide()
            QMessageBox.about(self, "Info", "Jestes gotowy aby rozpoczac gre")

    def build_ships_from_matrix(self):
        for x in range(10):
            for y in range(9):
                if self.my_board[x][y] == 1:

                    if x % 2 != 0:
                        self.item = QGraphicsPixmapItem(QPixmap(self.STATEK))
                        self.item.setOffset(18+y*61, 21+(x*52))
                        self.scene.addItem(self.item)

                    elif x % 2 == 0:
                        self.item = QGraphicsPixmapItem(QPixmap(self.STATEK))
                        self.item.setOffset(49+y*61, 21+x*53)
                        self.scene.addItem(self.item)

    def build_shots_from_matrix(self):
        picture = 'res/cancel.png'
        for x in range(10):
            for y in range(9):

                if self.my_board[x][y] == 2 or self.my_board[x][y] == 3:

                    if x % 2 != 0:
                        self.item = QGraphicsPixmapItem(QPixmap(picture))
                        self.item.setOffset(16+y*61, 17+(x*52))
                        self.scene.addItem(self.item)

                    elif x % 2 == 0:
                        self.item = QGraphicsPixmapItem(QPixmap(picture))
                        self.item.setOffset(47+y*61, 16+x*53)
                        self.scene.addItem(self.item)

                self.build_ships_from_matrix()

    def build_random_matrix(self):
        self.dm.clear()
        self.ready_to_play = True
        self.set_X.hide()
        self.set_Y.hide()
        self.set_ship_btn.hide()
        self.my_board = np.zeros((10, 9))
        ships = 0
        while ships < 10:
            x = randint(0, 9)
            y = randint(0, 8)
            if self.my_board[x][y] == 0:
                self.my_board[x][y] = 1
                ships += 1
        self.build_ships_from_matrix()
        # self.state.append((self.my_board, self.enemies_board, self.my_points))

    def clear_board(self):
        self.dm.clear()

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
            if x not in range(11):
                x, y = 0, 0
            if y not in range(11):
                x, y = 0, 0
        except ValueError:
            x, y = 0, 0
        return x, y


if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    mw = MyWin()
    mw.show()

    sys.exit(qApp.exec_())

