import socket
import threading


class Server:

    def __init__(self, config: tuple):
        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(config)
        self.sock.listen(1)

    def print_msg(self, msg):
        print('\033[1;33m', end='')
        print(self.ip, ':', self.port, ': ', sep='')
        print(msg)
        print('\033[0m')

    def read_handler(self, conn):
        while True:
            buff = conn.recv(1024)
            if buff:
                self.print_msg(buff.decode('utf-8'))

    def run(self):
        conn, host_addr = self.sock.accept()
        print("[", host_addr[0], ":", host_addr[1], '] connected', sep='')

        reader = threading.Thread(target=self.read_handler, args=(conn,), daemon=True)
        reader.start()

        while True:
            send_buff = bytes(input(''), 'utf8')
            conn.send(send_buff)


if __name__ == '__main__':

    config = ('127.0.0.1', 1234)
    server = Server(config)
    server.run()
