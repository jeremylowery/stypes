import unittest
from .sequence import Array, List, Tuple, NamedTuple
from .spec import String
from .numeric import Integer
from .util import UnconvertedValue

class ListTestCase(unittest.TestCase):

    def test_mainline(self):
        spec = List([12, 15, 1, Integer(3)])
        string = b"jeremy      lowery         s031"
        value = spec.unpack(string)
        self.assertIsInstance(value, list)
        text_rec = ['jeremy', 'lowery', 's', 31]
        self.assertEqual(value, text_rec)
        self.assertEqual(value.pack(), string)

    def test_atom(self):
        spec = List([String(3), 1, 1])
        v = spec.unpack(b"")
        self.assertEqual(v.pack(), b' '*5)

    def test_slice(self):
        spec = List([1]*5)
        v = spec.unpack(b"")
        v[1] = "X"
        self.assertEqual(v[1], "X")
        v[2:4] = ["Y", "Z"]
        self.assertEqual(v, ["", "X", "Y", "Z", ""])

    def test_assign(self):
        spec = List([12, 15, 1, Integer(3)])
        value = spec.unpack(b"")
        value[3] = "4"

    def test_list(self):
        spec = List("1;1;2")
        value = ["A", "B", "EE"]
        self.assertEqual(spec.pack(value), b"ABEE")

    def test_pack(self):
        spec = List([1, 1, 10])
        data = ["Y", "N", "Bacon"]
        self.assertEqual(spec.pack(data), b"YNBacon     ")

    def test_convert(self):
        spec = List([Integer(5)])
        value = spec.unpack(b"00040")
        self.assertEqual(value, [40])

    def test_nested_array(self):
        spec = List([String(12),
                        String(15),
                        String(1),
                        String(3),
                        Array(3, String(4))])
        string = b"jeremy      lowery         s031000100020003"
        value = spec.unpack(string)
        expected = ['jeremy', 'lowery', 's', '031', ['0001', '0002', '0003']]
        self.assertEqual(value, expected)

    def test_sub_assignment(self):
        mint = Integer(1)
        spec = List([mint, mint, List([mint, mint, mint])])
        s = spec.unpack(b'')
        self.assertEqual(s, [None, None, [None, None, None]])

        s[:2] = ['3', '4']
        self.assertEqual(s[:2], [3, 4])

        s[2][0] = '1'
        self.assertEqual(s[2], [1, None, None])

        s[2][:] = ['9', '8', '70']
        self.assertEqual(s, [3, 4, [9, 8, 70]])

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
        string = b"jeremy      lowery         s031"
        value = spec.unpack(string)
        text_rec = ('jeremy', 'lowery', 's', 31)
        self.assertEqual(value, text_rec)
        self.assertEqual(value.pack(), string)

    def test_tuple_convert(self):
        spec = Tuple([Integer(5)])
        value = spec.unpack(b"00040")
        self.assertEqual(value, (40,))

class ArrayTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = Array(3, Integer(1))
        string = b"123"
        value = spec.unpack(string)
        self.assertEqual(value, [1, 2, 3])
        self.assertEqual(value.pack(), string)

class NamedTupleTestCase(unittest.TestCase):
    def setUp(self):
        self._spec = NamedTuple([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', Integer(3))
        ])

    def test_mainline(self):
        buf = b"jeremy      lowery         s 23"
        tup = self._spec.unpack(buf)
        self.assertEqual(tup.first_name, "jeremy")
        self.assertEqual(tup.last_name, "lowery")
        self.assertEqual(tup.middle_initial, "s")
        self.assertEqual(tup.age, 23)

        buf = b"jeremy      lowery         s023"
        self.assertEqual(tup.pack(), buf)

    def test_bad_data(self):
        buf = b"jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEqual(type(tup.age), UnconvertedValue)

    def test_has_unconverted(self):
        buf = b"jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEqual(tup.has_unconverted(), True)

    def test_unconverted_report(self):
        buf = b"jeremy      lowery         sX23"
        tup = self._spec.unpack(buf)
        self.assertEqual(tup.unconverted_report(), "Index 3: expecting all digits for integer, given=b'X23'")
        
if __name__ == '__main__': unittest.main()
