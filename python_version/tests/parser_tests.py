import unittest
from datetime import datetime
from python_version.parser.parser import Parser, ParseError


class TestParser(unittest.TestCase):

    def test_decode_size(self):
        parser = Parser(encoding='utf-8')
        msg_size = 0
        for size in parser.sector_size.values():
            msg_size += int(size)
        self.assertEqual(msg_size,
                         len(parser.encode(
                             author='-',
                             msg_type='message',
                             datetime=datetime.now().strftime("%H:%M:%S %d-%m-%y"),
                             content='-')
                         ))

    def test_parse_exceptions(self):
        parser = Parser(encoding='utf-8')
        with self.assertRaises(ParseError):
            parser.encode('-', '-', '-', '-')

    def test_decode_keys(self):
        parser = Parser(encoding='utf-8')
        msg_size = 0
        for size in parser.sector_size.values():
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
            content='test_message')
        decoded = parser.decode(encoded)

        self.assertEqual('author', decoded['author'])
        self.assertEqual('message', decoded['type'])
        self.assertEqual('test_message', decoded['content'])


if __name__ == '__main__':
    unittest.main()
