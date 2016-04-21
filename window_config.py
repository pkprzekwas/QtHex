from PyQt4.QtCore import Qt


class WindowConfig(object):
    
    @staticmethod
    def config(QMainWindow):
        '''
        Window UI configuration.
        '''
        QMainWindow = QMainWindow
        QMainWindow.setWindowTitle(QMainWindow.tr("Statki"))

        QMainWindow.ip_addr_field.setPlaceholderText("Podaj adres IP przeciwnika")
        QMainWindow.ip_addr_field.setAlignment(Qt.AlignCenter)
        QMainWindow.port_field.setPlaceholderText("Podaj port przeciwnika")
        QMainWindow.port_field.setAlignment(Qt.AlignCenter)

        QMainWindow.set_X.setPlaceholderText("Podaj wspolzedna Y statku")
        QMainWindow.set_X.setAlignment(Qt.AlignCenter)

        QMainWindow.set_Y.setPlaceholderText("Podaj wspolzedna X statku")
        QMainWindow.set_Y.setAlignment(Qt.AlignCenter)

        QMainWindow.x_field.setPlaceholderText("Podaj wspolzedna Y statku")
        QMainWindow.x_field.setAlignment(Qt.AlignCenter)

        QMainWindow.y_field.setPlaceholderText("Podaj wspolzedna X statku")
        QMainWindow.y_field.setAlignment(Qt.AlignCenter)