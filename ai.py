from random import randint
from PyQt4.QtGui import QGraphicsPixmapItem, QPixmap

class AI(object):

    def __init__(self, QMainWindow):
        self.game = QMainWindow
        self.clear_unused_fields()
        ships = 0
        while ships < 10:
            x = randint(0, 9)
            y = randint(0, 8)
            if self.game.enemies_board[x][y] == 0:
                self.game.enemies_board[x][y] = 1
                ships += 1

    def clear_unused_fields(self):
        self.game.connect_btn.hide()
        self.game.ip_addr_field.hide()
        self.game.port_field.hide()

    def make_move(self):
        if not self.game.is_my_turn:
            x = randint(0, 9)
            y = randint(0, 8)
            if self.game.my_board[x][y] not in range(2,4):
                if self.game.my_board[x][y] == 1:
                    self.game.my_board[x][y] = 2
                    picture = 'res/cancel.png'
                else:
                    self.game.my_board[x][y] = 3
                    picture = 'res/ok.png'

                if x % 2 != 0:
                    self.item = QGraphicsPixmapItem(QPixmap(picture))
                    self.item.setOffset(16+y*61, 17+(x*52))
                    self.game.scene.addItem(self.item)

                elif x % 2 == 0:
                    self.item = QGraphicsPixmapItem(QPixmap(picture))
                    self.item.setOffset(47+y*61, 16+x*53)
                    self.game.scene.addItem(self.item)

            print(self.game.enemies_board)
            print(self.game.my_board)
            self.game.is_my_turn = True


