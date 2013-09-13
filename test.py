
from cStringIO import StringIO
from decimal import Decimal
import unittest

import stypes as st

class APITestCase(unittest.TestCase):
    """ Tests using the public package interface """
    def test_unconverted_value(self):
        x = st.UnconvertedValue('as', 'not an integer')
        self.assertFalse(x)
        s = "<UnconvertedValue string='as' reason='not an integer'>"
        self.assertEquals(repr(x), s)
        self.assertEquals(str(x), "not an integer, given='as'")

    def test_readme1(self):
        from decimal import Decimal
        from stypes import NamedTuple, Integer, Numeric
        spec = NamedTuple([
            ('name', 10),
            ('age', Integer(3)),
            ('weight', Numeric('999V99'))])
        text = "Johnson    2109750"
        rec = spec.unpack(text)
        self.assertEquals(rec.name, 'Johnson')
        self.assertEquals(rec.age, 21)
        self.assertEquals(rec.weight, Decimal("97.5"))

    def test_readme2(self):
        from stypes import Array, Dict, Integer, Numeric
        spec = Dict([
            ('invoice_no', Integer(4)),
            ('total', Numeric("999.99")),
            ('items', Array(3, Dict([
                ('line_no', Integer(2)),
                ('item_no', Integer(5)),
                ('total', Numeric("999.99"))
                ])))])
        inv = "0001200.450100004002.000200006198.50"
        rec = spec.unpack(inv)
        self.assertEquals(rec, 
            {'invoice_no': 1,
             'items': [{'item_no': 4, 'line_no': 1, 'total': Decimal('2.00')},
                       {'item_no': 6, 'line_no': 2, 'total': Decimal('198.50')},
                       {'item_no': None, 'line_no': None, 'total': None}],
             'total': Decimal('200.45')})

        rec['items'][-1] = {
            'line_no': 3,
            'item_no': 10,
            'total': Decimal("20")}

        rec['total'] = sum(i['total'] for i in rec['items'])
        self.assertEquals(rec.pack(),
            '0001220.500100004002.000200006198.500300010020.00')

    def test_from_unpack_usage(self):
        layout = [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3)
        ]
        inp = "jeremy      lowery         s"
        rec = st.unpack(inp, layout)
        rec['last_name'] = 'smith'
        res = "jeremy      smith          s   "
        self.assertEquals(st.pack(rec, layout), res)
        self.assertEquals(rec.pack(), res)

    def test_standalone_usage(self):
        data = {
            'first_name': 'jeremy',
            'last_name': 'lowery',
            'middle_initial': 's',
            'age': '031',
            'colors': ['0001', '0002', '0003']
        }

        text = st.pack(data, [
            ('first_name', 12),
            ('last_name',  15),
            ('middle_initial', 1),
            ('age', 3),
            ('colors[3]', 4)
            ])
        
        inp = "jeremy      lowery         s031000100020003"
        self.assertEquals(text, inp)

    def test_edi_scenario(self):
        infspec = st.Dict([
            ('claim_number', 12),
            ('claim_status', st.MappedString(1, {'R':'', 'O':'', 'C':'C'})),
            ('state_claim_number', 25), 
            ('coverage_code', 4),
            ('first_name', 12),
            ('last_name', 18),
            ('middle_initial', 1),
            ('sex', st.MappedString(1, {'M': '1', 'F': '2', 'U': ' '})),
            ('dob', st.Date('%m/%d/%Y'))
        ])
        
        outfspec = st.Dict([
            ('group_nbr', 8),
            ('patient_id', 11),
            ('dob', st.Date('%Y%m%d')),
            ('last_name', 15),
            ('first_name', 12),
            ('middle_initial', 1),
            ('sex', 1),
            ('claim_number', 30),
            ('claim_status', 1)
        ])

        in_file_data = StringIO("""\
11D46C058179O                         WC  Cammy       Meyer              F05/21/1934
11D46C058315O                         WC  Dennis      Tony              EM02/01/1972
11D46C028315O                         WC  Jimmy       John-Boy          EX11/11/1944
""")
        out_file_data = StringIO()
        err_file = StringIO()
        for idx, line in enumerate(in_file_data):
            rec = infspec.unpack(line)
            if rec.has_unconverted():
                err_file.write("Could not process record on line %d.\n" % (idx+1))
                err_file.write(rec.unconverted_report())
                err_file.write("\n")
                continue
            for upper_field in ['last_name', 'first_name', 'middle_initial']:
                rec[upper_field] = rec[upper_field].upper()
            rec['patient_id'] = rec['claim_number']
            self.assertRaises(KeyError, outfspec.pack, rec)
            rec['group_nbr'] = '11111111'
            out_file_data.write(outfspec.pack(rec))
            out_file_data.write("\n")

        err_file.seek(0)
        # two lines of error. one for the record line and one for the field info
        self.assertEquals(len(list(err_file)), 2)

        # The output file has two records
        outr = '1111111111D46C0581719340521MEYER          CAMMY        211D46C058179                   \n1111111111D46C0583119720201TONY           DENNIS      E111D46C058315                   \n'

        self.assertEquals(out_file_data.getvalue(), outr)

if __name__ == '__main__': unittest.main()
