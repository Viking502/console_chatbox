import unittest
from datetime import datetime
from python_version.parser.parser import Parser, ParseError


class TestParser(unittest.TestCase):

    def test_decode_size(self):
        parser = Parser(encoding='utf-8')
        msg_size = 0
        for size in parser.sector_size.values():
            if isinstance(size, dict):
                size = size['message']['text']
            msg_size += int(size)
        self.assertEqual(msg_size,
                         len(parser.encode(
                             author='-',
                             msg_type='message',
                             datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
                             content={'text': '-'})
                         ))

    def test_parse_exceptions(self):
        parser = Parser(encoding='utf-8')
        with self.assertRaises(ParseError):
            parser.encode('-', '-', '-', {'text': '-'})

    def test_decode_keys(self):
        parser = Parser(encoding='utf-8')
        msg_size = 0
        for size in parser.sector_size.values():
            if isinstance(size, dict):
                size = size['message']['text']
            msg_size += int(size)
        decoded = parser.decode(bytes(msg_size))

        keys = ['author', 'type', 'datetime', 'content']
        for key, expected in zip(decoded.keys(), keys):
            self.assertEqual(expected, key)

    def test_coding(self):
        parser = Parser('utf-8')
        encoded = parser.encode(
            author='author',
            msg_type='message',
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content={'text': 'test_message'})
        decoded = parser.decode(encoded)

        self.assertEqual('author', decoded['author'])
        self.assertEqual('message', decoded['type'])
        self.assertEqual('test_message', decoded['content']['text'])

    def test_login(self):
        parser = Parser('utf-8')
        encoded = parser.encode(
            author='author',
            msg_type='login',
            datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
            content={'nick': 'abcd', 'password': '1234'})
        decoded = parser.decode(encoded)

        self.assertEqual('author', decoded['author'])
        self.assertEqual('login', decoded['type'])
        self.assertEqual('abcd', decoded['content']['nick'])
        self.assertEqual('1234', decoded['content']['password'])


if __name__ == '__main__':
    unittest.main()
