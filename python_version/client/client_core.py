import socket
from datetime import datetime
from python_version.parser.parser import ParseError, Parser


class ClientCore:

    encoding = 'utf-8'
    is_logged = False

    def __init__(self, default: tuple = None):
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)

        self.default_connection = default

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.parser = Parser(encoding=self.encoding)

    def connect(self, server_ip: str = None, server_port: int = None):
        if not server_ip or not server_port:
            if self.default_connection:
                server_ip, server_port = self.default_connection
            else:
                raise Exception('no server address provided')
        self.sock.connect((server_ip, server_port))

    def read(self):
        read_buff = self.sock.recv(1024)
        if read_buff:
            read_buff = self.parser.decode(read_buff)
            if read_buff['type'] == 'login_successful':
                self.is_logged = True
            return read_buff
        return None

    def write(self, msg_type: str, content: dict = None):
        self.sock.send(self.parser.encode(
            msg_type=msg_type,
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content=content
        ))

    def log_in(self, nick: str, password: str):
        self.write(msg_type="login", content={'nick': nick, 'password': password})

    def register(self, nick: str, password: str):
        self.write(msg_type="register", content={'nick': nick, 'password': password})

    def send_msg(self, message: str, receiver: str = '\\all'):
        self.write(msg_type="message", content={'author': '-', 'receiver': receiver, 'text': message})

    def disconnect(self):
        self.write(msg_type='disconnect')
        self.is_logged = False
