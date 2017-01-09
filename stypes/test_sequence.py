import unittest
from .sequence import Array, List, Tuple, NamedTuple
from .spec import String
from .numeric import Integer
from .util import UnconvertedValue

class ListTestCase(unittest.TestCase):

    def test_mainline(self):
        spec = List([12, 15, 1, Integer(3)])
        string = "jeremy      lowery         s031"
        value = spec.unpack(string)
        self.assertIsInstance(value, list)
        text_rec = ['jeremy', 'lowery', 's', 31]
        self.assertEquals(value, text_rec)
        self.assertEquals(value.pack(), string)

    def test_atom(self):
        spec = List([String(3), 1, 1])
        v = spec.unpack("")
        self.assertEquals(v.pack(), ' '*5)

    def test_slice(self):
        spec = List([1]*5)
        v = spec.unpack("")
        v[1] = "X"
        self.assertEquals(v[1], "X")
        v[2:4] = ["Y", "Z"]
        self.assertEquals(v, ["", "X", "Y", "Z", ""])

    def test_assign(self):
        spec = List([12, 15, 1, Integer(3)])
        value = spec.unpack("")
        value[3] = "4"

    def test_list(self):
        spec = List("1;1;2")
        value = ["A", "B", "EE"]
        self.assertEquals(spec.pack(value), "ABEE")

    def test_pack(self):
        spec = List([1, 1, 10])
        data = ["Y", "N", "Bacon"]
        self.assertEquals(spec.pack(data), "YNBacon     ")

    def test_convert(self):
        spec = List([Integer(5)])
        value = spec.unpack("00040")
        self.assertEquals(value, [40])

    def test_nested_array(self):
        spec = List([String(12),
                        String(15),
                        String(1),
                        String(3),
                        Array(3, String(4))])
        string = "jeremy      lowery         s031000100020003"
        value = spec.unpack(string)
        expected = ['jeremy', 'lowery', 's', '031', ['0001', '0002', '0003']]
        self.assertEquals(value, expected)

    def test_sub_assignment(self):
        mint = Integer(1)
        spec = List([mint, mint, List([mint, mint, mint])])
        s = spec.unpack('')
        self.assertEquals(s, [None, None, [None, None, None]])

        s[:2] = ['3', '4']
        self.assertEquals(s[:2], [3, 4])

        s[2][0] = '1'
        self.assertEquals(s[2], [1, None, None])

        s[2][:] = ['9', '8', '70']
        self.assertEquals(s, [3, 4, [9, 8, 70]])

        try:
            s[2][:] = [1, 2, 3, 4, 5, 6]
            self.assertTrue(False, 'Attempted to change size of list with : slice')
        except TypeError:
            pass

        try:
            s[2][:] = [1, 2]
            self.assertTrue(False, 'Attempted to change size of list with : slice')
        except TypeError:
            pass


class TupleTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = Tuple([12, 15, 1, Integer(3)])
        string = "jeremy      lowery         s031"
        value = spec.unpack(string)
        text_rec = ('jeremy', 'lowery', 's', 31)
        self.assertEquals(value, text_rec)
        self.assertEquals(value.pack(), string)

    def test_tuple_convert(self):
        spec = Tuple([Integer(5)])
        value = spec.unpack("00040")
        self.assertEquals(value, (40,))

class ArrayTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = Array(3, Integer(1))
        string = "123"
        value = spec.unpack(string)
        self.assertEquals(value, [1, 2, 3])
        self.assertEquals(value.pack(), string)

class NamedTupleTestCase(unittest.TestCase):
    def setUp(self):
        self._spec = NamedTuple([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', Integer(3))
        ])

    def test_mainline(self):
        buf = "jeremy      lowery         s 23"
        tup = self._spec.unpack(buf)
        self.assertEquals(tup.first_name, "jeremy")
        self.assertEquals(tup.last_name, "lowery")
        self.assertEquals(tup.middle_initial, "s")
        self.assertEquals(tup.age, 23)
        
        buf = "jeremy      lowery         s023"
        self.assertEquals(tup.pack(), buf)

    def test_bad_data(self):
        buf = "jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEquals(type(tup.age), UnconvertedValue)

    def test_has_unconverted(self):
        buf = "jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEquals(tup.has_unconverted(), True)

    def test_unconverted_report(self):
        buf = "jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEquals(tup.unconverted_report(), "Index 3: expecting all digits for integer, given='X23'")
        
if __name__ == '__main__': 
    unittest.main()
