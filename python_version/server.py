import socket
import threading
from datetime import datetime


class Server:

    def __init__(self, config: tuple):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(config)
        self.sock.listen(12)

        self.hosts = []

    def print_msg(self, addr, msg):
        print(f'\033[1;33m{addr[0]}:{addr[1]}: {datetime.now().strftime("%H:%M:%S %d-%m-%y")}\n{msg}\033[0m')

    def read_handler(self, conn, addr):
        while True:
            buff = conn.recv(1024)
            if buff:
                self.print_msg(addr, buff.decode("utf-8"))
                for host in self.hosts:
                    if host['conn'] != conn:
                        host['conn'].send(buff)

    def run(self):
        while True:
            conn, host_addr = self.sock.accept()
            self.hosts.append({'addr': host_addr, 'conn': conn})
            print(f'({host_addr[0]}:{host_addr[1]}) has connected')

            reader = threading.Thread(target=self.read_handler, args=(conn, host_addr), daemon=True)
            reader.start()


if __name__ == '__main__':

    config = ('0.0.0.0', 1111)
    server = Server(config)
    server.run()
