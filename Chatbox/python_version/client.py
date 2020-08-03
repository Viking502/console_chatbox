import socket
import threading


class Client:

    def __init__(self, config):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.encoding = 'utf-8'
        self.is_running = False

    def print_msg(self, msg):
        print('\033[1;33m', self.ip, ':', self.port, '\033[0m', sep='')
        print(msg)

    def read_handler(self):
        while self.is_running:
            read_buff = self.sock.recv(1024)
            if read_buff:
                read_buff = read_buff.decode(self.encoding)
                if read_buff == 'exit':
                    self.is_running = False
                self.print_msg(read_buff)

    def write_handler(self):
        while self.is_running:
            self.print_msg('')
            send_buff = input('> ')
            if send_buff == 'exit':
                self.is_running = False
            self.sock.send(bytes(send_buff, self.encoding))

    def run(self):
        self.is_running = True
        with self.sock as sock:
            sock.connect((self.ip, self.port))
            print('connected with server')

            reader = threading.Thread(target=self.read_handler)
            reader.start()

            writer = threading.Thread(target=self.write_handler)
            writer.start()

            reader.join()
            writer.join()

        print('connection closed')


if __name__ == '__main__':
    config = ('127.0.0.1', 1111)
    client = Client(config)
    client.run()
