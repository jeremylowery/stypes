import datetime
import unittest

from .date import Date, Datetime

class DateTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Date("%Y%m%d")

    def test_from_bytes(self):
        self.assertEqual(self._s.from_bytes(b"20040101"), datetime.date(2004, 1, 1))

    def test_width(self):
        self.assertEqual(self._s.width, 8)

    def test_to_bytes(self):
        v = datetime.date(2004, 1, 1)
        self.assertEqual(self._s.to_bytes(v), b"20040101")

class DateTimeTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Datetime("%Y%m%d %H%M%S")
        
    def test_from_bytes(self):
        self.assertEqual(self._s.from_bytes(b"20100502 133025"), datetime.datetime(2010, 5, 2, 13, 30, 25))

    def test_to_bytes(self):
        self.assertEqual(self._s.to_bytes(datetime.datetime(2010, 5, 2, 13, 30, 25)), b"20100502 133025")

    def test_width(self):
        self.assertEqual(self._s.width, 15)

if __name__ == '__main__': unittest.main()
