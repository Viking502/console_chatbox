import socket
from datetime import datetime
from python_version.parser.parser import ParseError, Parser


class ClientCore:

    encoding = 'utf-8'
    is_logged = False
    wait_for_response = False

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
        self.wait_for_response = False
        if read_buff:
            read_buff = self.parser.decode(read_buff)
            if read_buff['type'] == 'authorized':
                self.is_logged = True
            return read_buff
        return None

    def write(self, msg_type: str, content: dict = None):
        self.sock.send(self.parser.encode(
            author=self.ip,
            msg_type=msg_type,
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content=content
        ))

    def log_in(self, nick: str, password: str):
        self.wait_for_response = True
        self.write(msg_type="login", content={'nick': nick, 'password': password})

    def send_msg(self, message: str):
        self.write(msg_type="message", content={'text': message})

    def disconnect(self):
        self.write(msg_type='disconnect')
        self.is_logged = False
