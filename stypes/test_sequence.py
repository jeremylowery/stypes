
import unittest
from .sequence import Array, List, Tuple, NamedTuple
from .spec import Scalar
from .numeric import Integer

class ListTestCase(unittest.TestCase):

    def test_mainline(self):
        spec = List([12, 15, 1, Integer(3)])
        string = "jeremy      lowery         s031"
        value = spec.parse(string)
        text_rec = ['jeremy', 'lowery', 's', '031']
        self.assertEquals(value, text_rec)

        value = value.from_text()
        typed_rec = ['jeremy', 'lowery', 's', 31]
        self.assertEquals(value, typed_rec)

        value = value.to_text()
        self.assertEquals(value, text_rec)
        self.assertEquals(value.format(), string)

    def test_list(self):
        spec = List("1;1;2")
        value = ["A", "B", "EE"]
        self.assertEquals(spec.format(value), "ABEE")

    def test_format(self):
        spec = List([1, 1, 10])
        data = ["Y", "N", "Bacon"]
        self.assertEquals(spec.format(data), "YNBacon     ")

    def test_convert(self):
        spec = List([Integer(5)])
        value = spec.expand("00040")
        self.assertEquals(value, [40])

    def test_nested_array(self):
        spec = List([Scalar(12),
                        Scalar(15),
                        Scalar(1),
                        Scalar(3),
                        Array(3, Scalar(4))])
        string = "jeremy      lowery         s031000100020003"
        value = spec.parse(string)
        expected = ['jeremy', 'lowery', 's', '031', ['0001', '0002', '0003']]
        self.assertEquals(value, expected)

class TupleTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = Tuple([12, 15, 1, Integer(3)])
        string = "jeremy      lowery         s031"
        value = spec.parse(string)
        text_rec = ('jeremy', 'lowery', 's', '031')
        self.assertEquals(value, text_rec)

        value = value.from_text()
        typed_rec = ('jeremy', 'lowery', 's', 31)
        self.assertEquals(value, typed_rec)

        value = value.to_text()
        self.assertEquals(value, text_rec)
        self.assertEquals(value.format(), string)

    def test_tuple_convert(self):
        spec = Tuple([Integer(5)])
        value = spec.expand("00040")
        self.assertEquals(value, (40,))

class NamedTupleTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = NamedTuple([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', Integer(3))
        ])
        buf = "jeremy      lowery         s 23"
        tup = spec.parse(buf)
        self.assertEquals(tup.first_name, "jeremy")
        self.assertEquals(tup.last_name, "lowery")
        self.assertEquals(tup.middle_initial, "s")
        self.assertEquals(tup.age, " 23")
        
        tup = tup.from_text()
        self.assertEquals(tup.age, 23)

        tup = tup.to_text()
        self.assertEquals(tup.age, "023")
        buf = "jeremy      lowery         s023"
        self.assertEquals(tup.format(), buf)

if __name__ == '__main__': 
    unittest.main()
