import PySide2.QtWidgets as QtW
from PySide2.QtCore import Qt, Slot, Signal
import sys
import threading
from python_version.client.client_core import ClientCore


class ChatWidget(QtW.QWidget):

    msg_signal = Signal(dict)

    def __init__(self, config: dict):
        QtW.QWidget.__init__(self)

        # initialize gui
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

        # initialize backend
        self.core = ClientCore(config)
        self.core.connect()

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()
        self.send_button.clicked.connect(self.send_msg)

    def send_msg(self):
        msg = self.send_box.toPlainText()
        self.send_box.clear()
        if msg == '\\exit':
            self.core.disconnect()
            self.update_messages(
                {'author': '', 'message': 'Disconnected', 'timestamp': ''}
            )
        else:
            self.core.write(msg=msg)

    @Slot()
    def update_messages(self, new_msg: dict):
        message = QtW.QLabel(f'{new_msg["author"]} - {new_msg["timestamp"]}\n{new_msg["message"]}')
        message.setAlignment(Qt.AlignTop)
        message.setStyleSheet("QLabel { border: 2px solid rgb(200, 200, 200)}")
        self.messages_box.addWidget(message)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def read_handler(self):
        while True:
            read_buff = self.core.read()
            if read_buff:
                print(read_buff)
                if read_buff['type'] == 'message':
                    self.msg_signal.emit(
                        {'author': read_buff['author'],
                         'message': read_buff['content'],
                         'timestamp': read_buff['datetime']}
                    )

    def send_disconnect_msg(self) -> int:
        self.core.disconnect()
        return 0


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)

    # set ip and port of server
    config = ('0.0.0.0', 1111)

    widget = ChatWidget(config)
    widget.resize(1200, 900)
    widget.msg_signal.connect(widget.update_messages)
    widget.show()

    sys.exit([app.exec_(), widget.send_disconnect_msg()])
