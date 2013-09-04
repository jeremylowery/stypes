import unittest

from .mapping import Dict, OrderedDict
from .numeric import Integer, Numeric, NumericFormatError
from .sequence import Array
from .spec import Scalar

class OrderedDictTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = OrderedDict([
            ('first_name', Scalar(12)),
            ('last_name',  Scalar(15)),
            ('middle_initial', Scalar(1)),
            ('age', Scalar(3)),
            ('colors', Array(3, Integer(4)))])
        inp = "jeremy      lowery         s031000100020003"
        rec = spec.unpack(inp)
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')
        self.assertEquals(rec['age'], '031')
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])
        self.assertEquals(rec.items(), [
            ('first_name', 'jeremy'),
            ('last_name', 'lowery'),
            ('middle_initial', 's'),
            ('age', '031'),
            ('colors', ['0001', '0002', '0003'])
        ])

        rec = rec.from_text()
        self.assertEquals(rec['colors'], [1, 2, 3])
        rec = rec.to_text()
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])

class DictTestCase(unittest.TestCase):
    def test_mainline(self):
        spec = Dict([
            ('first_name', Scalar(12)),
            ('last_name',  Scalar(15)),
            ('middle_initial', Scalar(1)),
            ('age', Scalar(3)),
            ('colors', Array(3, Integer(4)))])
        inp = "jeremy      lowery         s031000100020003"
        rec = spec.unpack(inp)
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')
        self.assertEquals(rec['age'], '031')
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])
        rec = rec.from_text()
        self.assertEquals(rec['colors'], [1, 2, 3])
        rec = rec.to_text()
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])

    def test_unpack_with_explicit_type_spec(self):
        spec = Dict([
            ('first_name', Scalar(12)),
            ('last_name',  Scalar(15)),
            ('middle_initial', Scalar(1)),
            ('age', Scalar(3)),
            ('colors', Array(3, Scalar(4)))])
        inp = "jeremy      lowery         s031000100020003"
        rec = spec.unpack(inp)
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')
        self.assertEquals(rec['age'], '031')
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])

    def test_unpack_with_structured_data_spec(self):
        spec = Dict([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ])
        inp = "jeremy      lowery         s"
        rec = spec.unpack(inp)
        self.assertFalse(rec.convert_errors())
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')

    def test_unpack_with_string_spec(self):
        inp = "YYNGOT CUT OF"
        rec = Dict("a;b;c;msg:100").unpack(inp)
        self.assertEquals(rec['msg'], 'GOT CUT OF')

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
            rec = spec.unpack(line)
    
    def test_array_unpack(self):
        expected = {'color': ['a', 'b', 'c']}

        # explicit as a pair
        spec = Dict([(('color', 3), 1)])
        self.assertEquals(spec.unpack("abc"), expected)
        
        # Given as a string
        spec = Dict("color[3]")
        self.assertEquals(spec.unpack("abc"), expected)

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
        text = "jeremyloweryM100 elm stbelton, tx"
        r = spec.unpack(text)
        self.assertEquals(r['demo']['first_name'], 'jeremy')
        self.assertEquals(r['demo']['last_name'], 'lowery')
        self.assertEquals(r['demo']['sex'], 'M')
        self.assertEquals(r['address']['line_1'], '100 elm st')
        self.assertEquals(r['address']['line_2'], 'belton, tx')

if __name__ == '__main__': unittest.main()
