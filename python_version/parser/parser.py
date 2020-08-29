from struct import pack, unpack


class ParseError(Exception):
    pass


class Parser:
    sector_size = {'type': 0x02, 'datetime': 0x11,
                   'content': {
                       'message': {'author': 0x10, 'receiver': 0x10, 'text': 0x80},
                       'server_message': {'text': 0x80},
                       'register': {'nick': 0x10, 'password': 0x20},
                       'login': {'nick': 0x10, 'password': 0x20}
                        }
                   }
    type_code = {
        'message': b'\x00\x00', 'register': b'\x00\x01', 'login': b'\x00\x02', 'disconnect': b'\x00\x03',
        'register_successful': b'\x00\x04', 'login_successful': b'\x00\x05', 'server_message': b'\x00\x06'
                 }

    def __init__(self, encoding):
        self.encoding = encoding

    def encode(self, msg_type: str, datetime: str, content: dict = None):
        encoded = bytes()
        for key, val in zip(self.sector_size.keys(), [msg_type, datetime, content]):
            if key == 'type':
                try:
                    encoded += self.type_code[val]
                except KeyError:
                    raise ParseError
            elif key == 'content':
                if msg_type in self.sector_size['content'].keys():
                    if val is None:
                        raise ParseError
                    for arg, cont in val.items():
                        try:
                            encoded +=\
                                pack(f"{self.sector_size[key][msg_type][arg]}s", bytes(cont, encoding=self.encoding))
                        except TypeError:
                            raise ParseError
            else:
                try:
                    encoded += pack(f"{self.sector_size[key]}s", bytes(val, encoding=self.encoding))
                except TypeError:
                    raise ParseError
        return encoded

    def decode(self, message: bytes) -> dict:
        decoded_msg = {key: None for key in self.sector_size.keys()}

        for sector, value in self.sector_size.items():
            if sector == 'content':
                if decoded_msg['type'] in self.sector_size['content'].keys():
                    decoded_msg[sector] = dict()
                    content = value[decoded_msg['type']]
                    for arg, size in content.items():
                        try:
                            decoded_msg[sector][arg] =\
                                unpack(f'{size}s', message[:size])[0].decode(self.encoding).strip('\x00')
                        except TypeError:
                            print("key:", arg, " value:", size)
                            raise ParseError()
                        message = message[size:]
                else:
                    decoded_msg.pop('content', None)
            else:
                if sector == 'type':
                    decoded_msg[sector] = \
                        list(self.type_code.keys())[int.from_bytes(message[:value], 'big')]
                else:
                    try:
                        decoded_msg[sector] = unpack(f'{value}s', message[:value])[0].decode(self.encoding).strip('\x00')
                    except TypeError:
                        raise ParseError()
                message = message[value:]

        return decoded_msg
