import json
import socket
import struct
import logging
import time
import threading

logger = logging.getLogger("jsonSocket")
logger.setLevel(logging.DEBUG)
FORMAT = '[%(asctime)-15s][%(levelname)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT)


class JsonSocket(object):
    def __init__(self, address='127.0.0.1', port=5007):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.socket
        self._timeout = None
        self._address = address
        self._port = port

    def sendObj(self, obj):
        msg = json.dumps(obj)
        if self.socket:
            frmt = '=%ds' % len(msg)
            msg = bytes(msg, 'utf-8')
            packedMsg = struct.pack(frmt, msg)
            packedHdr = struct.pack('=I', len(packedMsg))

            self._send(packedHdr)
            self._send(packedMsg)

    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.conn.send(msg[sent:])

    def _read(self, size):
        data = ''
        while len(data) < size:
            dataTmp = self.conn.recv(size-len(data))
            dataTmp = dataTmp.decode()
            data += dataTmp
            if dataTmp == '':
                raise RuntimeError("socket connection broken")
        return data

    def _msgLength(self):
        d = self._read(4)
        d = bytes(d, 'utf-8')
        s = struct.unpack('=I', d)
        return s[0]

    def readObj(self):
        size = self._msgLength()
        data = self._read(size)
        frmt = "=%ds" % size
        data = bytes(data, 'utf-8')
        msg = struct.unpack(frmt, data)
        msg = list(msg)
        msg[0] = msg[0].decode()
        return json.loads(msg[0])

    def close(self):
        logger.debug("closing main socket")
        self._closeConnection()
        self._closeSocket()
        if self.socket is not self.conn:
            logger.debug("closing connection socket")
            self._closeConnection()

    def _closeSocket(self):
        self.socket.close()

    def _closeConnection(self):
        self.conn.close()

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = timeout
        self.socket.settimeout(timeout)

    def _get_address(self):
        return self._address

    def _set_address(self, address):
        pass

    def _get_port(self):
        return self._port

    def _set_port(self, port):
        self._port = port
        pass

    timeout = property(_get_timeout, _set_timeout, doc='Get/set the socket timeout')
    address = property(_get_address, _set_address, doc='read only property socket address')
    port = property(_get_port, _set_port, doc='read only property socket port')


class JsonServer(JsonSocket):
    def __init__(self, address='127.0.0.1', port=5007):
        super(JsonServer, self).__init__(address, port)
        self._port = port
        self._bind()

    def _bind(self):
        try:
            self.socket.bind( (self.address,self.port) )
        except:
            self._set_port(10000)
            self.socket.bind( (self.address,self.port) )
    def _listen(self):
        self.socket.listen(1)

    def _accept(self):
        return self.socket.accept()

    def acceptConnection(self):
        self._listen()

        self.conn, addr = self._accept()
        self.conn.settimeout(self.timeout)
        logger.debug("connection accepted, conn socket (%s,%d)" % (addr[0],addr[1]))


class JsonClient(JsonSocket):
    def __init__(self, address='127.0.0.1', port=5007):
        super(JsonClient, self).__init__(address, port)

    def connect(self):
        for i in range(10):
            try:
                self.socket.connect( (self.address, self.port) )
            except socket.error as msg:
                logger.error("SockThread Error: %s" % msg)
                time.sleep(3)
                continue
            logger.info("...Socket Connected")
            return True
        return False


class ThreadedServer(threading.Thread, JsonServer):
    def __init__(self, address='127.0.0.1', port=5007, **kwargs):
        threading.Thread.__init__(self)
        JsonServer.__init__(self, address, port)
        self._isAlive = False

    def _processMessage(self, obj):
        """ virtual method """
        pass

    def run(self):
        while self._isAlive:
            try:
                self.acceptConnection()
            except socket.timeout as e:
                logger.debug("socket.timeout: %s" % e)
                continue
            except Exception as e:
                logger.exception(e)
                continue

            while self._isAlive:
                try:
                    obj = self.readObj()
                    self._processMessage(obj)
                except socket.timeout as e:
                    logger.debug("socket.timeout: %s" % e)
                    continue
                except Exception as e:
                    logger.exception(e)
                    self._closeConnection()
                    break

    def start(self):
        self._isAlive = True
        super(ThreadedServer, self).start()

    def stop(self):
        """ The life of the dead is in the memory of the living """
        self._isAlive = False