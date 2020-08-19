import socket
from json import loads


class ClientCore:

    msg_codes = ['\\exit']
    encoding = 'utf-8'

    def __init__(self, config: dict):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.ip, self.port))

    def read(self):
        read_buff = self.sock.recv(1024)
        if read_buff:
            return loads(read_buff.decode(self.encoding))
        return None

    def write(self, msg: str):
        self.sock.send(bytes(msg, self.encoding))
        if msg in self.msg_codes:
            return msg
        return None
