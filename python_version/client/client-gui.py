import PySide2.QtWidgets as QtW
from PySide2.QtCore import Qt, Slot, Signal
import sys
import threading
import socket
from json import loads


class ChatWidget(QtW.QWidget):

    msg_signal = Signal(dict)

    def __init__(self, config):
        QtW.QWidget.__init__(self)
        self.layout = QtW.QGridLayout()

        self.scroll = QtW.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(self.scroll, 0, 0, 3, -1)

        self.wrapper = QtW.QWidget()
        self.scroll.setWidget(self.wrapper)

        self.messages_box = QtW.QVBoxLayout()
        self.messages_box.setAlignment(Qt.AlignTop)
        self.wrapper.setLayout(self.messages_box)

        self.send_box = QtW.QTextEdit("")
        self.send_box.setFixedHeight(self.height() // 8)
        self.layout.addWidget(self.send_box, 3, 0)

        self.send_button = QtW.QPushButton("send!")
        self.send_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.layout.addWidget(self.send_button, 3, 1)

        self.setLayout(self.layout)

        self.ip, self.port = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.encoding = 'utf-8'
        self.sock.connect((self.ip, self.port))

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()

        self.send_button.clicked.connect(self.send_msg)

    def send_msg(self):
        msg = self.send_box.toPlainText()
        self.send_box.clear()
        self.sock.send(bytes(msg, self.encoding))
        if msg == '\\exit':
            self.update_messages(
                {'author': '', 'message': 'Disconnected', 'timestamp': ''}
            )

    @Slot()
    def update_messages(self, new_msg: dict):
        message = QtW.QLabel(f'{new_msg["author"]} - {new_msg["timestamp"]}\n{new_msg["message"]}')
        message.setAlignment(Qt.AlignTop)
        message.setStyleSheet("QLabel { border: 2px solid rgb(200, 200, 200)}")
        self.messages_box.addWidget(message)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def read_handler(self):
        while True:
            read_buff = self.sock.recv(1024)
            if read_buff:
                read_buff = loads(read_buff.decode(self.encoding))
                print(read_buff)
                self.msg_signal.emit(
                    {'author': read_buff['auth'], 'message': read_buff['msg'], 'timestamp': read_buff['time']}
                )

    def send_disconnect_msg(self) -> int:
        self.sock.send(bytes('\\exit', self.encoding))
        return 0


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)

    # set ip and port of server
    config = ('0.0.0.0', 1111)

    widget = ChatWidget(config)
    widget.resize(1200, 900)
    widget.show()

    widget.msg_signal.connect(widget.update_messages)

    sys.exit([app.exec_(), widget.send_disconnect_msg()])
