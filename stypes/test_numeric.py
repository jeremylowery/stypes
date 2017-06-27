from decimal import Decimal
import unittest

from .mapping import Dict
from .numeric import Integer, Numeric, NumericFormatError

class IntegerTestCase(unittest.TestCase):
    def test_integer_conversion(self):
        rtype = Dict([
            ('x', Integer(3)),
            ('y', Integer(3))
         ])
        rec = rtype.unpack(" 12 50")
        self.assertEquals(rec['x'], 12)
        self.assertEquals(rec['y'], 50)

        rec['x'] = 20
        self.assertEquals(rec.pack(), "020050")

class NumericTestCase(unittest.TestCase):
    def test_conversion(self):
        # make a field definition
        line_item = Dict([
            ('invoice_id', Integer(4)),
            ('item_nbr',   Integer(2)),
            ('price', Numeric("999V99")),
            ('sales_tax', Numeric("99V99")),
            ('total', Numeric("999V99"))
        ])

        # reading some text off of disk
        text = "100101550000525"
        rec = line_item.unpack(text)

        # the text was a little short, but that's ok
        self.assertFalse(rec.has_unconverted())

        # do some computation to the record and write it
        # back to disk
        rec['total'] = rec['price'] + rec['sales_tax']
        new_text = rec.pack()

        # Let's read the newly stored record and be sure the
        # computed total was saved correctly
        new_rec = line_item.unpack(new_text)
        self.assertEquals(new_rec['total'], rec['total'])

    def test_width(self):
        def test(nfmt, width):
            self.assertEquals(Numeric(nfmt).width, width)
        test("999V99", 5)
        test("999.99", 6)
        test("9,999",  5)
        test("9(4)V99",6)
        test("9(4).9(3)", 8)

    def test_from_bytes(self):
        def test(nfmt, inp, outp):
            self.assertEquals(Numeric(nfmt).from_bytes(inp), Decimal(outp))

        test("999V99", "00025", ".25")
        test("999.99", "  2.25", "2.25")
        test("9,999", "1,234", "1234")
        test("9(4)V99", "030054", "300.54")
        test("9(4).9(3)", "0300.054", "300.054")

        test("S999.99", "   2.25", "2.25")
        test("S999.99", "-  2.25", "-2.25")
        test("999.99S", "  2.25-", "-2.25")

    def test_to_bytes(self):
        def test(nfmt, inp, outp):
            f = Numeric(nfmt)
            self.assertEquals(f.to_bytes(Decimal(inp)), outp)
        test("999V99",  ".25", "00025")
        test("999.99",  "2.25", "002.25")
        test("9,999",  "1234", "1,234")
        test("9(4)V99",  "300.54", "030054")
        test("9(4).9(3)", "300.054", "0300.054")

        test("999.99",  "2.2", "002.20")
        # Overflow
        test("999.99",  "1000", "000.00")

        test("S999.99", "2.25",  " 002.25")
        test("S999.99", "-2.25", "-002.25")
        test("999.99S", "-2.25", "002.25-")

    def test_invalid_pack(self):
        def test(*a):
            self.assertRaises(NumericFormatError, Numeric, *a)
        test("(4")
        test("asdf")
        #test("99.99.")

    def test_invalid_sign(self):
        def test(*a):
            self.assertRaises(NumericFormatError, Numeric, *a)
        test("SS")
        test("9(S")

if __name__ == '__main__': unittest.main()
