import unittest
from datetime import datetime
from python_version.parser.parser import Parser, ParseError


class TestParser(unittest.TestCase):

    def test_decode_size(self):
        parser = Parser(encoding='utf-8')
        msg_size = parser.sector_size['type'] + parser.sector_size['datetime'] \
                    + parser.sector_size['content']['message']['text'] \
                    + parser.sector_size['content']['message']['receiver'] \
                    + parser.sector_size['content']['message']['author']

        self.assertEqual(msg_size,
                         len(parser.encode(
                             msg_type='message',
                             datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
                             content={'author': '-', 'receiver': '-', 'text': '-'}))
                         )

    def test_parse_exceptions(self):
        parser = Parser(encoding='utf-8')
        with self.assertRaises(ParseError):
            parser.encode('-', '-', {'author': '-', 'receiver': '-', 'text': '-'})

    def test_decode_keys(self):
        parser = Parser(encoding='utf-8')
        msg_size = 0
        for size in parser.sector_size.values():
            if isinstance(size, dict):
                msg_size += int(size['message']['text'])\
                            + int(size['message']['author'])\
                            + int(size['message']['receiver'])
            else:
                msg_size += int(size)
        decoded = parser.decode(bytes(msg_size))

        keys = ['type', 'datetime', 'content']
        for key, expected in zip(decoded.keys(), keys):
            self.assertEqual(expected, key)

    def test_coding(self):
        parser = Parser('utf-8')
        encoded = parser.encode(
            msg_type='message',
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content={'author': 'author', 'receiver': 'receiver', 'text': 'test_message'})
        decoded = parser.decode(encoded)

        self.assertEqual('message', decoded['type'])
        self.assertEqual('author', decoded['content']['author'])
        self.assertEqual('receiver', decoded['content']['receiver'])
        self.assertEqual('test_message', decoded['content']['text'])

    def test_login(self):
        parser = Parser('utf-8')
        encoded = parser.encode(
            msg_type='login',
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content={'nick': 'abcd', 'password': '1234'})
        decoded = parser.decode(encoded)

        self.assertEqual('login', decoded['type'])
        self.assertEqual('abcd', decoded['content']['nick'])
        self.assertEqual('1234', decoded['content']['password'])

    def test_disconnect(self):
        parser = Parser('utf-8')
        encoded = parser.encode(
            msg_type='disconnect',
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y")
        )
        decoded = parser.decode(encoded)

        self.assertEqual('disconnect', decoded['type'])


if __name__ == '__main__':
    unittest.main()
