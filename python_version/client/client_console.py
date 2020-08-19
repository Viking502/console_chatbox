import threading
from client_core import ClientCore


class Client:

    def __init__(self, config: dict):
        self.core = ClientCore(config)
        self.is_running = False

    @staticmethod
    def print_msg(data: dict):
        print(f'\033[1;33m{data["auth"]} - {data["time"]}\n{data["msg"]}\033[0m')

    def read_handler(self):
        while True:
            read_buff = self.core.read()
            if read_buff:
                self.print_msg(read_buff)

    def write_handler(self):
        while self.is_running:
            send_buff = input()
            code = self.core.write(send_buff)
            if code == '\\exit':
                self.is_running = False

    def run(self):
        self.core.connect()
        self.is_running = True
        print('connected with server')

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()

        self.write_handler()
        print('connection closed')


if __name__ == '__main__':
    config = ('0.0.0.0', 1111)
    client = Client(config)
    client.run()
