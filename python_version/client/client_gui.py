import PySide2.QtWidgets as QtW
from PySide2.QtCore import Qt, Slot, Signal
import sys
import threading
from python_version.client.client_core import ClientCore


class ServerConnectionLayout:

    def __init__(self, entry_func: callable, default_config: tuple = None):

        self.entry_func = entry_func
        default_ip, default_port = None, None
        if default_config:
            default_ip, default_port = default_config

        self.layout = QtW.QVBoxLayout()
        self.layout.setMargin(100)
        self.layout.setAlignment(Qt.AlignCenter)

        header = QtW.QLabel('Connect to server')
        self.layout.addWidget(header)

        self.addr_box = QtW.QLineEdit()
        if default_ip:
            self.addr_box.setText(default_ip)
        self.addr_box.setPlaceholderText('server address IPv4')
        self.addr_box.setMaximumWidth(260)
        self.layout.addWidget(self.addr_box)

        self.port_box = QtW.QLineEdit()
        self.port_box.setPlaceholderText('server port')
        if default_port:
            self.port_box.setText(str(default_port))
        self.port_box.setMaximumWidth(260)
        self.layout.addWidget(self.port_box)

        self.connect_button = QtW.QPushButton('Connect')
        self.connect_button.setFixedWidth(80)
        self.connect_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.connect_button.clicked.connect(self.open_connection)
        self.layout.addWidget(self.connect_button)

    def open_connection(self):
        ip = self.addr_box.text()
        try:
            port = int(self.port_box.text())
        except ValueError:
            port = None
        self.entry_func(ip=ip, port=port)

    def get(self):
        return self.layout


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

        self.send_box = QtW.QTextEdit()
        self.send_box.setPlaceholderText('message')
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

        self.layout = QtW.QFormLayout()
        self.layout.setSpacing(20)
        self.layout.setMargin(100)
        self.layout.setAlignment(Qt.AlignCenter)

        # nick
        self.nick_layout = QtW.QHBoxLayout()
        self.login_label = QtW.QLabel('nick: ')
        self.login_label.setFixedWidth(120)
        self.nick_layout.addWidget(self.login_label)
        self.login_box = QtW.QLineEdit()
        self.login_box.setPlaceholderText('nick')
        self.login_box.setMaximumWidth(260)
        self.nick_layout.addWidget(self.login_box)

        self.layout.addRow(self.nick_layout)
        # password
        self.pass_layout = QtW.QHBoxLayout()
        self.pass_label = QtW.QLabel('password: ')
        self.pass_label.setFixedWidth(120)
        self.pass_layout.addWidget(self.pass_label)
        self.pass_box = QtW.QLineEdit()
        self.pass_box.setEchoMode(QtW.QLineEdit.Password)
        self.pass_box.setPlaceholderText('password')
        self.pass_box.setMaximumWidth(260)
        self.pass_layout.addWidget(self.pass_box)

        self.layout.addRow(self.pass_layout)
        # buttons
        self.buttons_layout = QtW.QHBoxLayout()
        self.login_button = QtW.QPushButton("log_in")
        self.login_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.login_button.setMaximumWidth(80)
        self.login_button.clicked.connect(self.log_in)
        self.buttons_layout.addWidget(self.login_button)

        self.register_button = QtW.QPushButton("register")
        self.register_button.setStyleSheet("QPushButton:hover { background-color: rgb(200, 200, 200) }")
        self.register_button.setMaximumWidth(80)
        self.register_button.clicked.connect(self.register)
        self.buttons_layout.addWidget(self.register_button)

        self.layout.addRow(self.buttons_layout)
        # messages from server
        self.server_msg = QtW.QLabel()
        self.server_msg.setAlignment(Qt.AlignTop)
        self.server_msg.setStyleSheet("QLabel {color: rgb(200, 20, 20)}")
        self.layout.addWidget(self.server_msg)

    def log_in(self):
        nick = self.login_box.text()
        password = self.pass_box.text()
        self.core.log_in(nick=nick, password=password)

    def register(self):
        nick = self.login_box.text()
        password = self.pass_box.text()
        self.core.register(nick=nick, password=password)

    @Slot()
    def update_server_msg(self, new_msg: dict):
        self.server_msg.setText(f"{new_msg['timestamp']}\n{new_msg['message']}")

    def get(self):
        return self.layout


class ChatWidget(QtW.QWidget):

    msg_signal = Signal(dict)

    def __init__(self, config: tuple = None):
        QtW.QWidget.__init__(self)

        # initialize backend
        self.core = ClientCore(config)
        self.reader = threading.Thread(target=self.read_handler, daemon=True)

        # initialize gui
        self.layouts_stack = QtW.QStackedLayout()

        self.messages_layout = MessagesLayout(self.height(), self.core)
        self.messages_widget = QtW.QWidget()
        self.messages_widget.setLayout(self.messages_layout.get())

        self.login_layout = LoginLayout(self.core)
        self.login_widget = QtW.QWidget()
        self.login_widget.setLayout(self.login_layout.get())

        self.connection_layout = ServerConnectionLayout(
            entry_func=self.run_connection,
            default_config=default_connection
        )
        self.connection_widget = QtW.QWidget()
        self.connection_widget.setLayout(self.connection_layout.get())

        self.layouts_stack.addWidget(self.connection_widget)
        self.layouts_stack.addWidget(self.login_widget)
        self.layouts_stack.addWidget(self.messages_widget)

        self.msg_signal.connect(self.login_layout.update_server_msg)
        self.msg_signal.connect(self.messages_layout.update_messages)
        self.setLayout(self.layouts_stack)

    def run_connection(self, ip, port):
        is_connected = False
        try:
            self.core.connect(server_ip=ip, server_port=port)
            is_connected = True
        except ConnectionRefusedError:
            print(f'can\'t connect to server at {ip}:{port}')

        if is_connected:
            self.layouts_stack.setCurrentWidget(self.login_widget)
            self.reader.start()

    def read_handler(self):
        while True:
            read_buff = self.core.read()
            if read_buff:
                print(read_buff)
                if read_buff['type'] == 'message':
                    self.msg_signal.emit(
                        {'author': read_buff['author'],
                         'message': read_buff['content']['text'],
                         'timestamp': read_buff['datetime']}
                    )
                elif read_buff['type'] == 'login_successful':
                    self.layouts_stack.setCurrentWidget(self.messages_widget)

    def send_disconnect_msg(self) -> int:
        self.core.disconnect()
        return 0


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)

    # set ip and port of server
    default_connection = ('0.0.0.0', 1111)

    widget = ChatWidget(default_connection)
    widget.resize(1200, 900)
    widget.show()

    sys.exit([app.exec_(), widget.send_disconnect_msg()])
