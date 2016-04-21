import numpy as np
import xml.etree.ElementTree as ET

import jsonSocket


class Server(jsonSocket.ThreadedServer):
    def __init__(self, q_main_window, address='127.0.0.1', port=5007):
        jsonSocket.ThreadedServer.__init__(self, address, port)
        self.mw = q_main_window
        super(Server, self).__init__()
        self.timeout = 2.0

    def _processMessage(self, obj):
        """ virtual method """
        if obj != '':
            x = obj.get("x")
            y = obj.get("y")
            if x == "T":
                self.mw.enemies_board[self.mw.send[0]][self.mw.send[1]] = 2
                print("Trafiony")
                self.mw.my_points += 1
                if self.mw.my_points == 5:
                    print("Wygrales")
            elif x == "P":
                self.mw.enemies_board[self.mw.send[0]][self.mw.send[1]] = 3
                print("Podlo")
            elif x == "W":
                print("Wygrales")
            else:
                if self.mw.my_board[x][y] == 1:
                    self.mw.my_board[x][y] = 2
                    self.mw.client.sendObj({"x": "T", "y": 1})
                else:
                    self.mw.my_board[x][y] = 3
                    self.mw.client.sendObj({"x": "P", "y": 1})

            print(self.mw.my_board)
            print(self.mw.enemies_board)
            my_board = np.copy(self.mw.my_board)
            enemies_board = np.copy(self.mw.enemies_board)

            self.mw.tie += 1
            doc = ET.SubElement(self.mw.root, "sitting")
            ET.SubElement(doc, "my_board", name="defense").text = str(self.mw.my_board)
            ET.SubElement(doc, "enemies_board", name="offense").text = str(self.mw.my_board)

            self.mw.state.append((my_board, enemies_board, self.mw.my_points))
            self.mw.is_my_turn = True
