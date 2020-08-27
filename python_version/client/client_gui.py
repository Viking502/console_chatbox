import PySide2.QtWidgets as QtW
from PySide2.QtCore import Qt, Slot, Signal
import sys
import threading
from python_version.client.client_core import ClientCore


class MessagesLayout:

    def __init__(self, high, core):
        self.core = core

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
        self.send_box.setFixedHeight(high // 8)
        self.layout.addWidget(self.send_box, 3, 0)

        self.send_button = QtW.QPushButton("send!")
        self.send_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.layout.addWidget(self.send_button, 3, 1)
        self.send_button.clicked.connect(self.send_msg)

    def get(self):
        return self.layout

    def send_msg(self):
        msg = self.send_box.toPlainText()
        self.send_box.clear()
        if msg == '\\exit':
            self.core.disconnect()
            self.update_messages(
                {'author': '', 'message': 'Disconnected', 'timestamp': ''}
            )
        else:
            self.core.send_msg(message=msg)

    @Slot()
    def update_messages(self, new_msg: dict):
        message = QtW.QLabel(f'{new_msg["author"]} - {new_msg["timestamp"]}\n{new_msg["message"]}')
        message.setAlignment(Qt.AlignTop)
        message.setStyleSheet("QLabel { border: 2px solid rgb(200, 200, 200)}")
        self.messages_box.addWidget(message)
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())


class LoginLayout:

    def __init__(self, core):
        self.core = core

        self.layout = QtW.QGridLayout()

        self.login_label = QtW.QLabel('nick: ')
        self.login_label.setFixedHeight(60)
        self.login_label.setFixedWidth(280)
        self.layout.addWidget(self.login_label, 0, 0)
        self.login_box = QtW.QTextEdit()
        self.login_box.setFixedHeight(60)
        self.login_box.setFixedWidth(280)
        self.layout.addWidget(self.login_box, 0, 1)

        self.pass_label = QtW.QLabel('password: ')
        self.layout.addWidget(self.pass_label, 1, 0)
        self.pass_box = QtW.QTextEdit()
        self.pass_box.setFixedHeight(60)
        self.pass_box.setFixedWidth(280)
        self.layout.addWidget(self.pass_box, 1, 1)

        self.login_button = QtW.QPushButton("log_in")
        self.login_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.login_button.clicked.connect(self.log_in)
        self.layout.addWidget(self.login_button, 2, 1)

    def log_in(self):
        nick = self.login_box.toPlainText()
        password = self.pass_box.toPlainText()
        print(nick, password)
        self.core.log_in(nick=nick, password=password)

    def get(self):
        return self.layout


class ChatWidget(QtW.QWidget):

    msg_signal = Signal(dict)

    def __init__(self, config: dict):
        QtW.QWidget.__init__(self)

        # initialize backend
        self.core = ClientCore(config)
        self.core.connect()

        reader = threading.Thread(target=self.read_handler, daemon=True)
        reader.start()

        # initialize gui
        self.messages_layout = MessagesLayout(self.height(), self.core)
        self.messages_widget = QtW.QWidget()
        self.messages_widget.setLayout(self.messages_layout.get())

        self.login_layout = LoginLayout(self.core)
        self.login_widget = QtW.QWidget()
        self.login_widget.setLayout(self.login_layout.get())

        self.layouts_stack = QtW.QStackedLayout()
        self.layouts_stack.addWidget(self.login_widget)
        self.layouts_stack.addWidget(self.messages_widget)

        self.setLayout(self.layouts_stack)

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
                elif read_buff['type'] == 'authorized':
                    self.layouts_stack.setCurrentWidget(self.messages_widget)

    def send_disconnect_msg(self) -> int:
        self.core.disconnect()
        return 0


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)

    # set ip and port of server
    config = ('0.0.0.0', 1111)

    widget = ChatWidget(config)
    widget.resize(1200, 900)
    widget.msg_signal.connect(widget.messages_layout.update_messages)
    widget.show()

    sys.exit([app.exec_(), widget.send_disconnect_msg()])
