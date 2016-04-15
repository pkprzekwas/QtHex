from PyQt4.QtGui import QGraphicsPixmapItem, QPixmap


class DrawMap:
    def __init__(self, scene):
        self.scene = scene
        # self.scene1 = scene1
        self._generate_fields()

    def _generate_fields(self):
        self.item = QGraphicsPixmapItem(QPixmap('res/map.jpg'))
        self.scene.addItem(self.item)

    def clear(self):
        self._generate_fields()




