
from cStringIO import StringIO
from decimal import Decimal
import unittest

import stypes as st

class FormatSequenceTestCase(unittest.TestCase):
    def test_list(self):
        spec = st.List("1;1;2")
        value = ["A", "B", "EE"]
        self.assertEquals(spec.format(value), "ABEE")

    def test_format(self):
        spec = st.List([1, 1, 10])
        data = ["Y", "N", "Bacon"]
        self.assertEquals(spec.format(data), "YNBacon     ")
        
class ParseSequenceTestCase(unittest.TestCase):
    def test_with_structued_data_spec(self):
        spec = st.List([st.Scalar(12),
                        st.Scalar(15),
                        st.Scalar(1),
                        st.Scalar(3),
                        st.Array(3, st.Scalar(4))])
        string = "jeremy      lowery         s031000100020003"
        value = spec.parse(string)
        expected = ['jeremy', 'lowery', 's', '031', ['0001', '0002', '0003']]
        self.assertEquals(value, expected)

    def test_tuple(self):
        spec = st.Tuple([12, 15, 1, 3])
        string = "jeremy      lowery         s031"
        value = spec.parse(string)
        expected = ('jeremy', 'lowery', 's', '031')
        self.assertEquals(value, expected)

    def test_list_convert(self):
        spec = st.List([st.Integer(5)])
        value = spec.expand("00040")
        self.assertEquals(value, [40])

    def test_tuple_convert(self):
        spec = st.Tuple([st.Integer(5)])
        value = spec.expand("00040")
        self.assertEquals(value, (40,))

    def test_named_tuple(self):
        spec = st.NamedTuple([
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', st.Integer(3))
        ])
        buf = "jeremy      lowery         s 23"
        tup = spec.parse(buf)
        self.assertEquals(tup.first_name, "jeremy")
        self.assertEquals(tup.last_name, "lowery")
        self.assertEquals(tup.middle_initial, "s")
        self.assertEquals(tup.age, " 23")
        
        tup = tup.from_text()
        self.assertEquals(tup.age, 23)

class ParseDictTestCase(unittest.TestCase):
    def test_parse_with_explicit_type_spec(self):
        spec = st.Dict([
            ('first_name', st.Scalar(12)),
            ('last_name',  st.Scalar(15)),
            ('middle_initial', st.Scalar(1)),
            ('age', st.Scalar(3)),
            ('colors', st.Array(3, st.Scalar(4)))])
        inp = "jeremy      lowery         s031000100020003"
        rec = spec.parse(inp)
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')
        self.assertEquals(rec['age'], '031')
        self.assertEquals(rec['colors'], ['0001', '0002', '0003'])

    def test_parse_with_structured_data_spec(self):
        spec = [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ]
        inp = "jeremy      lowery         s"
        rec = st.parse(inp, spec)
        self.assertFalse(rec.convert_errors())
        self.assertEquals(rec['first_name'], 'jeremy')
        self.assertEquals(rec['last_name'], 'lowery')
        self.assertEquals(rec['middle_initial'], 's')

    def test_parse_with_string_spec(self):
        inp = "YYNGOT CUT OF"
        rec = st.parse(inp, "a;b;c;msg:100")
        self.assertEquals(rec['msg'], 'GOT CUT OF')

    def test_multiparse_with_data_structure_spec(self):
        fields = [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ]
        buf = ("jeremy      lowery         s 23\n"
               "tom         jones          V X3\n")
        for line in buf.split("\n"):
            rec = st.parse(line, fields)
    
    def test_array_parse(self):
        expected = {'color': ['a', 'b', 'c']}
        self.assertEquals(st.parse("abc", [(('color', 3), 1)]), expected)
        self.assertEquals(st.parse("abc", "color[3]"), expected)

    def test_sub_with_structured_data_spec(self):
        spec = st.Dict([
            ('demo', st.Dict([
                ('first_name', 6),
                ('last_name', 6),
                ('sex', 1)
            ])),
            ('address', st.Dict([
                ('line_1', 10),
                ('line_2', 10)
            ]))
        ])
        text = "jeremyloweryM100 elm stbelton, tx"
        r = st.parse(text, spec)
        self.assertEquals(r['demo']['first_name'], 'jeremy')
        self.assertEquals(r['demo']['last_name'], 'lowery')
        self.assertEquals(r['demo']['sex'], 'M')
        self.assertEquals(r['address']['line_1'], '100 elm st')
        self.assertEquals(r['address']['line_2'], 'belton, tx')

    def _test_sub_with_string_spec(self):
        spec = """demo:{first_name:6;last_name:6;sex:1};
                   address:{line_1:10;line_2:10}"""
        text = "jeremyloweryM100 elm stbelton, tx"
        r = st.parse(text, spec)

class FormatTestCase(unittest.TestCase):
    def test_from_parse_usage(self):
        layout = [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ]
        inp = "jeremy      lowery         s"
        rec = st.parse(inp, layout)
        rec['last_name'] = 'smith'
        res = "jeremy      smith          s   "
        self.assertEquals(st.format(rec, layout), res)
        self.assertEquals(rec.format(), res)

    def test_standalone_usage(self):
        data = {
            'first_name': 'jeremy',
            'last_name': 'lowery',
            'middle_initial': 's',
            'age': '031',
            'colors': ['0001', '0002', '0003']
        }

        text = st.format(data, [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3),
            ('colors[3]', 4)
            ])
        
        inp = "jeremy      lowery         s031000100020003"
        self.assertEquals(text, inp)

class ConversionTestCase(unittest.TestCase):
    def test_integer_conversion(self):
        trec = {'x': '12', 'y': '50', 'color': 'red'}
        rtype = st.Dict([
            ('x', st.Integer(3)),
            ('y', st.Integer(3))
         ])
        rec = rtype.from_text(trec)
        self.assertEquals(rec['x'], 12)
        self.assertEquals(rec['y'], 50)

        rec['x'] = 20
        trec = rtype.to_text(rec)
        self.assertEquals(trec['x'], '020')

class NumericTestCase(unittest.TestCase):
    def test_conversion(self):
        # make a field definition
        line_item = st.Dict([
            ('invoice_id', st.Integer(4)),
            ('item_nbr',   st.Integer(2)),
            ('price', st.Numeric("999V99")),
            ('sales_tax', st.Numeric("99V99")),
            ('total', st.Numeric("999V99"))
        ])

        # reading some text off of disk
        text = "100101550000525"
        rec = line_item.expand(text)

        # the text was a little short, but that's ok
        self.assertFalse(rec.convert_errors())

        # do some computation to the record and write it
        # back to disk
        rec['total'] = rec['price'] + rec['sales_tax']
        new_text = line_item.squash(rec)

        # Let's read the newly stored record and be sure the
        # computed total was saved correctly
        new_rec = line_item.expand(new_text)
        self.assertEquals(new_rec['total'], rec['total'])

    def test_width(self):
        def test(nfmt, width):
            self.assertEquals(st.Numeric(nfmt).width, width)
        test("999V99", 5)
        test("999.99", 6)
        test("9,999",  5)
        test("9(4)V99",6)
        test("9(4).9(3)", 8)
        
    def test_from_text(self):
        def test(nfmt, inp, outp):
            self.assertEquals(st.Numeric(nfmt).from_text(inp), Decimal(outp))

        test("999V99", "00025", ".25")
        test("999.99", "  2.25", "2.25")
        test("9,999", "1,234", "1234")
        test("9(4)V99", "030054", "300.54")
        test("9(4).9(3)", "0300.054", "300.054")

    def test_to_text(self):
        def test(nfmt, inp, outp):
            f = st.Numeric(nfmt)
            self.assertEquals(f.to_text(Decimal(inp)), outp)
        test("999V99",  ".25", "00025")
        test("999.99",  "2.25", "002.25")
        test("9,999",  "1234", "1,234")
        test("9(4)V99",  "300.54", "030054")
        test("9(4).9(3)", "300.054", "0300.054")

        test("999.99",  "2.2", "002.20")
        # Overflow
        test("999.99",  "1000", "000.00")

    def test_invalid_format(self):
        def test(*a):
            self.assertRaises(st.NumericFormatError, st.Numeric, *a)
        test("(4")
        test("asdf")
        #test("99.99.")

if __name__ == '__main__': unittest.main()
