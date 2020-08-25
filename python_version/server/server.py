import socket
import threading
from datetime import datetime
from python_version.parser.parser import ParseError, Parser
from python_version.server.accounts import Accounts


class Server:
    encoding = 'utf-8'

    def __init__(self, config: tuple):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(config)
        self.sock.listen(12)
        self.hosts = []
        self.parser = Parser(self.encoding)
        self.accounts = Accounts(db_name='users.db', encoding=self.encoding)
        self.accounts.create_tables()

    def remove_host(self, ip_addr: str):
        for idx, host in enumerate(self.hosts):
            if host['addr'] == ip_addr:
                del self.hosts[idx]
                break

    @staticmethod
    def print_msg(message: dict):
        print(f'\033[1;33m{message["author"]}: {message["datetime"]}\n{message["content"]}\033[0m')

    def read_handler(self, conn: socket.socket, addr: str):
        while True:
            buff = conn.recv(1024)
            if buff:
                try:
                    decoded_msg = self.parser.decode(buff)
                except ParseError:
                    print('parse error')
                    break
                if decoded_msg['type'] == 'disconnect':
                    self.remove_host(addr)
                    print(f'({addr}) has disconnected')
                    break
                encoded_msg = self.parser.encode(
                    author=addr,
                    msg_type='message',
                    datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
                    content=decoded_msg['content']
                    )
                self.print_msg(decoded_msg)
                for host in self.hosts:
                    host['conn'].send(encoded_msg)

    def log_user(self):
        pass

    def register_user(self):
        pass

    def handle_connection(self, conn, host_addr):

        self.read_handler(conn, host_addr)

    def run(self):
        while True:
            conn, host_addr = self.sock.accept()
            host_addr = f'{host_addr[0]}:{host_addr[1]}'
            self.hosts.append({'conn': conn, 'addr': host_addr})
            print(f'({host_addr}) has connected')

            reader = threading.Thread(target=self.handle_connection, args=(conn, host_addr), daemon=True)
            reader.start()


if __name__ == '__main__':

    config = ('0.0.0.0', 1111)
    server = Server(config)
    server.run()
