from PyQt4.QtGui import QGraphicsPixmapItem, QPixmap


class DrawMap:
    def __init__(self, scene, scene1):
        self.scene = scene
        self.scene1 = scene1
        self._generate_fields()

    def _generate_fields(self):

        for i in range(5):
            for j in range(5):
                self.item = QGraphicsPixmapItem(QPixmap('res/hex1.gif'))
                if j % 2 == 0:
                        self.item.setOffset(i*110+55, j*70)
                else:
                    self.item.setOffset(i*110, j*70)
                self.scene.addItem(self.item)

        for i in range(5):
            for j in range(5):
                self.item = QGraphicsPixmapItem(QPixmap('res/hex1.gif'))
                if j % 2 == 0:
                    self.item.setOffset(i*110+55, j*70)
                else:
                    self.item.setOffset(i*110, j*70)
                self.scene1.addItem(self.item)
        self.item = QGraphicsPixmapItem(QPixmap('res/map.jpg'))
        self.scene.addItem(self.item)

        self.item = QGraphicsPixmapItem(QPixmap('res/map.jpg'))
        self.scene1.addItem(self.item)



