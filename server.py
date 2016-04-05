import jsonSocket


class Server(jsonSocket.ThreadedServer):
    def __init__(self, address='127.0.0.1', port=5007):
        jsonSocket.ThreadedServer.__init__(self, address, port)
        super(Server, self).__init__()
        self.timeout = 2.0

    def _processMessage(self, obj):
        """ virtual method """
        if obj != '':
            x = obj.get("x")
            y = obj.get("y")
            x, y = self._parser(x, y)
            print(x, y)

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