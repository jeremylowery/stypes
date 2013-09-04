
from cStringIO import StringIO
from decimal import Decimal
import unittest

import stypes as st

class APITestCase(unittest.TestCase):
    """ Tests using the public package interface """
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

if __name__ == '__main__': unittest.main()
