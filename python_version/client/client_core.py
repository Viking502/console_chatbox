import socket
from datetime import datetime
from python_version.parser.parser import ParseError, Parser


class ClientCore:

    encoding = 'utf-8'

    def __init__(self, config: dict):
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.server_ip, self.server_port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parser = Parser(encoding=self.encoding)

    def connect(self):
        self.sock.connect((self.server_ip, self.server_port))

    def read(self):
        read_buff = self.sock.recv(1024)
        if read_buff:
            return self.parser.decode(read_buff)
        return None

    def write(self, msg: str = '', msg_type: str = 'message'):
        self.sock.send(self.parser.encode(
            author=self.ip,
            msg_type=msg_type,
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content=msg
        ))

    def disconnect(self):
        self.write(msg_type='disconnect')
