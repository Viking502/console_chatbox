import threading
import time
from python_version.client.client_core import ClientCore


class Client:

    def __init__(self, default_connection: tuple = None):
        self.core = ClientCore(default_connection)
        self.is_running = False
        self.wait_for_response = False

    @staticmethod
    def print_msg(data: dict):
        print(f'\033[1;33m{data["author"]} - {data["datetime"]}\n{data["content"]["text"]}\033[0m')

    def read_handler(self):
        while True:
            read_buff = self.core.read()
            if read_buff:
                self.wait_for_response = False
                if read_buff['type'] == 'message':
                    self.print_msg(read_buff)
                elif read_buff['type'] == 'login_successful':
                    print('\033[1;32mLogged successfully\033[0m')
                elif read_buff['type'] == 'register_successfully':
                    print('\033[1;32mLogged successfully\033[0m')

    def write_handler(self):
        while self.is_running:
            send_buff = input()
            if send_buff == '\\exit':
                self.core.disconnect()
                self.is_running = False
            else:
                self.core.send_msg(message=send_buff)

    def run(self):

        if self.core.default_connection:
            ip, port = self.core.default_connection
        else:
            print(f'provide sever address')
            ip = input('IPv4: >_')
            port = input('port: >_')
            try:
                port = int(port)
            except ValueError:
                port = None
        try:
            self.core.connect(ip, port)
        except ConnectionRefusedError:
            print(f'can\'t connect to server at {ip}:{port}')
            return 1

        self.is_running = True
        print('connected with server')

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()

        print('''
YOU ARE NOT LOGGIN IN\n
to log in type:
\033[1;46m\\login $nick $password\033[0m
to register new user type:
\033[1;46m\\register $nick $password\033[0m
to exit type:
\033[1;46m\\exit\033[0m
        ''')
        wait_duration = 5
        while not self.core.is_logged:
            cmd = input(">_").split()
            if cmd[0] in ['\\login', '\\register']:
                cmd, nick, password = cmd
            else:
                cmd = cmd[0]

            if cmd == '\\login':
                self.wait_for_response = True
                self.core.log_in(nick=nick, password=password)
            elif cmd == '\\register':
                self.wait_for_response = True
                self.core.register(nick=nick, password=password)
            elif cmd == '\\exit':
                self.core.disconnect()
                break
            else:
                print(f'No command {cmd}')

            while self.wait_for_response and wait_duration > 0:
                print('waiting for response..')
                time.sleep(1)
                wait_duration -= 1

        if self.core.is_logged:
            self.write_handler()

        print('connection closed')


if __name__ == '__main__':
    config = ('0.0.0.0', 1111)
    client = Client()
    client.run()
