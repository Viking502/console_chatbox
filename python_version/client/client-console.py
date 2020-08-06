import socket
import threading
from json import loads


class Client:

    def __init__(self, config: dict):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.encoding = 'utf-8'
        self.is_running = False

    @staticmethod
    def print_msg(data: dict):
        print(f'\033[1;33m{data["auth"]} - {data["time"]}\n{data["msg"]}\033[0m')

    def read_handler(self):
        while True:
            read_buff = self.sock.recv(1024)
            if read_buff:
                read_buff = loads(read_buff.decode(self.encoding))
                self.print_msg(read_buff)

    def write_handler(self):
        while self.is_running:
            send_buff = input()
            if send_buff == '\\exit':
                self.is_running = False
            self.sock.send(bytes(send_buff, self.encoding))

    def run(self):
        self.is_running = True
        with self.sock as sock:
            sock.connect((self.ip, self.port))
            print('connected with server')

            reader = threading.Thread(target=self.read_handler, daemon=True)
            reader.start()

            # writer = threading.Thread(target=self.write_handler, daemon=True)
            # writer.start()
            self.write_handler()

        print('connection closed')


if __name__ == '__main__':
    config = ('0.0.0.0', 1111)
    client = Client(config)
    client.run()
