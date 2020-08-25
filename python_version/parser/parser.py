from struct import pack, unpack


class ParseError(Exception):
    pass


class Parser:
    sector_size = {'author': 0x10, 'type': 0x02, 'datetime': 0x11, 'content': 0x80}
    type_code = {'message': b'\x00\x00', 'register': b'\x00\x01', 'login': b'\x00\x02', 'disconnect': b'\x00\x03'}

    def __init__(self, encoding):
        self.encoding = encoding

    def encode(self, author: str, msg_type: str, datetime: str, content: str):
        encoded = bytes()
        for key, val in zip(self.sector_size.keys(), [author, msg_type, datetime, content]):
            if key == 'type':
                try:
                    encoded += self.type_code[val]
                except KeyError:
                    raise ParseError
            else:
                encoded += pack(f"{self.sector_size[key]}s", bytes(val, encoding=self.encoding))
        return encoded

    def decode(self, message: bytes) -> dict:
        decoded_msg = {key: None for key in self.sector_size.keys()}

        for sector, size in self.sector_size.items():
            if sector == 'type':
                decoded_msg[sector] = \
                    list(self.type_code.keys())[int.from_bytes(message[:size], 'big')]
            else:
                try:
                    decoded_msg[sector] = unpack(f'{size}s', message[:size])[0].decode(self.encoding).strip('\x00')
                except TypeError:
                    raise ParseError()
            message = message[size:]
        return decoded_msg
