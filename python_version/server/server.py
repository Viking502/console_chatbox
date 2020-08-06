import socket
import threading
from datetime import datetime
import json


class Server:

    def __init__(self, config: tuple):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(config)
        self.sock.listen(12)

        self.hosts = []

    def remove_host(self, ip_addr):
        for idx, host in enumerate(self.hosts):
            if host['addr'] == ip_addr:
                del self.hosts[idx]
                break

    @staticmethod
    def print_msg(message):
        print(f'\033[1;33m{message["auth"]}: {message["time"]}\n{message["msg"]}\033[0m')

    def read_handler(self, conn, addr):
        while True:
            buff = conn.recv(1024)
            if buff:
                if buff.decode('utf-8') == '\\exit':
                    self.remove_host(addr)
                    print(f'({addr}) has disconnected')
                    break
                encoded_msg = bytes(json.dumps(
                    {'auth': addr,
                     'msg': buff.decode('utf-8'),
                     'time': datetime.now().strftime("%H:%M:%S %d-%m-%y")}
                ), 'utf-8')
                self.print_msg(json.loads(encoded_msg.decode('utf-8')))
                for host in self.hosts:
                    host['conn'].send(encoded_msg)

    def run(self):
        while True:
            conn, host_addr = self.sock.accept()
            host_addr = f'{host_addr[0]}:{host_addr[1]}'
            self.hosts.append({'addr': host_addr, 'conn': conn})
            print(f'({host_addr}) has connected')

            reader = threading.Thread(target=self.read_handler, args=(conn, host_addr), daemon=True)
            reader.start()


if __name__ == '__main__':

    config = ('0.0.0.0', 1111)
    server = Server(config)
    server.run()
