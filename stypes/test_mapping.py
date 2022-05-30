import unittest

from .mapping import Dict
from .odict import OrderedDict
from .numeric import Integer, Numeric, NumericFormatError
from .sequence import Array
from .spec import String

class OrderedDictTestCase(unittest.TestCase):
    def setUp(self):
        self._spec = OrderedDict([
            ('first_name', String(12)),
            ('last_name',  String(15)),
            ('middle_initial', String(1)),
            ('age', Integer(3)),
            ('colors', Array(3, Integer(4)))])

    def test_mainline(self):
        inp = b"jeremy      lowery         s031000100020003"
        rec = self._spec.unpack(inp)
        self.assertEqual(rec['first_name'], 'jeremy')
        self.assertEqual(rec['last_name'], 'lowery')
        self.assertEqual(rec['middle_initial'], 's')
        self.assertEqual(rec['age'], 31)
        self.assertEqual(rec['colors'], [1, 2, 3])
        self.assertEqual(list(rec.items()), [
            ('first_name', 'jeremy'),
            ('last_name', 'lowery'),
            ('middle_initial', 's'),
            ('age', 31),
            ('colors', [1, 2, 3])
        ])

        self.assertEqual(rec.pack(), inp)

    def test_update(self):
        inp = b"jeremy      lowery         s031000100020003"
        rec = self._spec.unpack(inp)
        rec['last_name'] = 'smith'
        outp = b"jeremy      smith          s031000100020003"
        self.assertEqual(rec.pack(), outp)
        try:
            del rec['last_name']
            self.assertTrue(False, 'deleting did not raise TypeError')
        except TypeError:
            pass

        try:
            rec.clear()
            self.assertTrue(False, 'clearing did not raise TypeError')
        except TypeError:
            pass

        rec.update({'age': '35', 'colors': ['2', '4', '3']})
        out = b'jeremy      smith          s035000200040003'
        self.assertEqual(rec.pack(), out)

class NDictTestCase(unittest.TestCase):
    def setUp(self):
        self._spec = Dict([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', Integer(3))])

    def test_foobar(self):
        inp = b"jeremy      lowery         s031"
        rec = self._spec.unpack(inp)
        self.assertEqual(rec['age'], 31)

    def test_update(self):
        inp = b"jeremy      lowery         s031000100020003"
        outp = b"jeremy      smith          s031"
        rec = self._spec.unpack(inp)
        rec['last_name'] = 'smith'
        self.assertEqual(rec.pack(), outp)
        try:
            del rec['last_name']
            self.assertTrue(False, 'deleting did not raise TypeError')
        except TypeError:
            pass

        try:
            rec.clear()
            self.assertTrue(False, 'clearing did not raise TypeError')
        except TypeError:
            pass

class DictTestCase(unittest.TestCase):
    def setUp(self):
        self._spec = Dict([
            ('first_name', String(12)),
            ('last_name',  String(15)),
            ('middle_initial', String(1)),
            ('age', Integer(3)),
            ('colors', Array(3, Integer(4)))])

    def test_mainline(self):
        inp = b"jeremy      lowery         s031000100020003"
        rec = self._spec.unpack(inp)
        self.assertEqual(rec['first_name'], 'jeremy')
        self.assertEqual(rec['last_name'], 'lowery')
        self.assertEqual(rec['middle_initial'], 's')
        self.assertEqual(rec['age'], 31)
        self.assertEqual(rec['colors'], [1, 2, 3])

    def test_assignment(self):
        inp = b"jeremy      lowery         s031000100020003"
        rec = self._spec.unpack(inp)
        rec['last_name'] = 'smith'
        rec['age'] = 30
        outp = b'jeremy      smith          s030000100020003'
        self.assertEqual(rec.pack(), outp)

    def test_sublist_assignment(self):
        rec = self._spec.unpack(b'')
        rec['colors'][:] = '123'

    def test_unpack_with_explicit_type_spec(self):
        spec = Dict([
            ('first_name', String(12)),
            ('last_name',  String(15)),
            ('middle_initial', String(1)),
            ('age', String(3)),
            ('colors', Array(3, String(4)))])
        inp = b"jeremy      lowery         s031000100020003"
        rec = spec.unpack(inp)
        self.assertEqual(rec['first_name'], 'jeremy')
        self.assertEqual(rec['last_name'], 'lowery')
        self.assertEqual(rec['middle_initial'], 's')
        self.assertEqual(rec['age'], '031')
        self.assertEqual(rec['colors'], ['0001', '0002', '0003'])

    def test_unpack_with_structured_data_spec(self):
        spec = Dict([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ])
        inp = b"jeremy      lowery         s"
        rec = spec.unpack(inp)
        self.assertEqual(rec['first_name'], 'jeremy')
        self.assertEqual(rec['last_name'], 'lowery')
        self.assertEqual(rec['middle_initial'], 's')

    def test_unpack_with_string_spec(self):
        inp = b"YYNGOT CUT OF"
        rec = Dict("a;b;c;msg:100").unpack(inp)
        self.assertEqual(rec['msg'], 'GOT CUT OF')

    def test_multiunpack_with_data_structure_spec(self):
        spec = Dict([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ])
        buf = ("jeremy      lowery         s 23\n"
               "tom         jones          V X3\n")
        for line in buf.split("\n"):
            rec = spec.unpack(line.encode())

    def test_array_unpack(self):
        expected = {'color': ['a', 'b', 'c']}

        # explicit as a pair
        spec = Dict([(('color', 3), 1)])
        self.assertEqual(spec.unpack(b"abc"), expected)

        # Given as a string
        spec = Dict("color[3]")
        self.assertEqual(spec.unpack(b"abc"), expected)

    def test_sub_with_structured_data_spec(self):
        spec = Dict([
            ('demo', Dict([
                ('first_name', 6),
                ('last_name', 6),
                ('sex', 1)
            ])),
            ('address', Dict([
                ('line_1', 10),
                ('line_2', 10)
            ]))
        ])
        text = b"jeremyloweryM100 elm stbelton, tx"
        r = spec.unpack(text)
        self.assertEqual(r['demo']['first_name'], 'jeremy')
        self.assertEqual(r['demo']['last_name'], 'lowery')
        self.assertEqual(r['demo']['sex'], 'M')
        self.assertEqual(r['address']['line_1'], '100 elm st')
        self.assertEqual(r['address']['line_2'], 'belton, tx')

if __name__ == '__main__': unittest.main()
