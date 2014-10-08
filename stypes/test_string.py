
import unittest

from .spec import BoxedString

class DateTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  BoxedString(5, 2)

    def test_to_bytes(self):
        self.assertEquals(self._s.to_bytes("aaaaa\r\nbbbbb"), "aaaaabbbbb")

    def test_to_trunc(self):
        self.assertEquals(self._s.to_bytes("aaaaavvvvv\r\nbbbbb"), "aaaaabbbbb")

    def test_width(self):
        self.assertEquals(self._s.width, 10)

    def test_from_bytes(self):
        self.assertEquals(self._s.from_bytes("aaaaabbbbb"), "aaaaa\r\nbbbbb")

