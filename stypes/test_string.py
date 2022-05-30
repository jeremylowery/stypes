
import unittest

from .spec import BoxedString

class DateTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  BoxedString(5, 2)

    def test_to_bytes(self):
        self.assertEqual(self._s.to_bytes("aaaaa\r\nbbbbb"), b"aaaaabbbbb")

    def test_to_trunc(self):
        self.assertEqual(self._s.to_bytes("aaaaavvvvv\r\nbbbbb"), b"aaaaabbbbb")

    def test_width(self):
        self.assertEqual(self._s.width, 10)

    def test_from_bytes(self):
        self.assertEqual(self._s.from_bytes(b"aaaaabbbbb"), "aaaaa\r\nbbbbb")

if __name__ == '__main__': unittest.main()
