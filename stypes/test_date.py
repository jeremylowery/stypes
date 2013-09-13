import datetime
import unittest

from .date import Date, Datetime

class DateTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Date("%Y%m%d")

    def test_from_text(self):
        self.assertEquals(self._s.from_text("20040101"), datetime.date(2004, 1, 1))

    def test_width(self):
        self.assertEquals(self._s.width, 8)

    def test_to_text(self):
        v = datetime.date(2004, 1, 1)
        self.assertEquals(self._s.to_text(v), "20040101")

class DateTimeTestCase(unittest.TestCase):
    def setUp(self):
        self._s =  Datetime("%Y%m%d %H%M%S")
        
    def test_from_text(self):
        self.assertEquals(self._s.from_text("20100502 133025"), datetime.datetime(2010, 5, 2, 13, 30, 25))

    def test_to_text(self):
        self.assertEquals(self._s.to_text(datetime.datetime(2010, 5, 2, 13, 30, 25)), "20100502 133025")

    def test_width(self):
        self.assertEquals(self._s.width, 15)
