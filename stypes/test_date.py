import datetime
import unittest

from .date import Date, Datetime

class DateTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Date("%Y%m%d")

    def test_from_bytes(self):
        self.assertEquals(self._s.from_bytes("20040101"), datetime.date(2004, 1, 1))

    def test_width(self):
        self.assertEquals(self._s.width, 8)

    def test_to_bytes(self):
        v = datetime.date(2004, 1, 1)
        self.assertEquals(self._s.to_bytes(v), "20040101")

class DateTimeTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Datetime("%Y%m%d %H%M%S")
        
    def test_from_bytes(self):
        self.assertEquals(self._s.from_bytes("20100502 133025"), datetime.datetime(2010, 5, 2, 13, 30, 25))

    def test_to_bytes(self):
        self.assertEquals(self._s.to_bytes(datetime.datetime(2010, 5, 2, 13, 30, 25)), "20100502 133025")

    def test_width(self):
        self.assertEquals(self._s.width, 15)
