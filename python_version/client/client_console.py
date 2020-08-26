import threading
import time
from python_version.client.client_core import ClientCore


class Client:

    def __init__(self, config: dict):
        self.core = ClientCore(config)
        self.is_running = False

    @staticmethod
    def print_msg(data: dict):
        print(f'\033[1;33m{data["author"]} - {data["datetime"]}\n{data["content"]["text"]}\033[0m')

    def read_handler(self):
        while True:
            read_buff = self.core.read()
            if read_buff:
                if read_buff['type'] == 'message':
                    self.print_msg(read_buff)
                else:
                    pass
                    # TODO different kind of messages

    def write_handler(self):
        while self.is_running:
            send_buff = input()
            if send_buff == '\\exit':
                self.core.disconnect()
                self.is_running = False
            else:
                self.core.send_msg(message=send_buff)

    def run(self):
        self.core.connect()
        self.is_running = True
        print('connected with server')

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()

        while not self.core.is_logged:
            print('LOG IN')
            nick = input('nick: ')
            password = input('password: ')
            self.core.log_in(nick=nick, password=password)
            wait_duration = 5
            while self.core.wait_for_response and wait_duration > 0:
                time.sleep(1)
                print('waiting for response..')
                wait_duration -= 1

        print('logged successfully')

        self.write_handler()
        print('connection closed')


if __name__ == '__main__':
    config = ('0.0.0.0', 1111)
    client = Client(config)
    client.run()
