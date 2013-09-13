Rich Type Library for Textual Data
==================================

**WARNING: This is alpha software and the interface is likely to change.**

stypes is a text parsing, conversion and formatting library written to
efficiently handle large fixed-width text record data files. Convert text
streams into dictionaries, lists, tuples, named tuples, ordered dictionaries
and more using text layout specifications.

One of the main design goals of the library was to handle legacy text-based
record data that is commonly found in COBOL system. Of course, the library
can be used to handle any fixed layout textual data.

A simple example of turning some text into a Named Tuple:

```python
from decimal import Decimal
from stypes import NamedTuple, Integer, Numeric
spec = NamedTuple([
	('name', 10),
	('age', Integer(3)),
	('weight', Numeric('999V99'))])
text = "Johnson    2109750"
rec = spec.unpack(text)
assert rec.name == 'Johnson'
assert rec.age == 21
assert rec.weight == Decimal("97.5")
```

And a more interesting example using nested data structures of a list of
records and actually updating a record.

```python
from stypes import Array, Dict, Integer, Numeric
item = Dict([('line_no', Integer(2)),
	('item_no', Integer(5)),
	('total', Numeric("999.99"))])
invoice = Dict([
    ('invoice_no', Integer(4)),
    ('total', Numeric("999.99")),
    ('items', Array(3, item))])
text = "0001200.450100004002.000200006198.50"
rec = invoice.unpack(inv)
# rec is now
  {'invoice_no': 1,
   'items': [{'item_no': 4, 'line_no': 1, 'total': Decimal('2.00')},
	     {'item_no': 6, 'line_no': 2, 'total': Decimal('198.50')},
	     {'item_no': None, 'line_no': None, 'total': None}],
   'total': Decimal('200.45')}

# Set the last invoice item
rec['items'][-1] = {
    'line_no': 3,
    'item_no': 10,
    'total': Decimal("20")}

# Update the invoice total
rec['total'] = sum(i['total'] for i in rec['items'])
print rec.pack()
# '0001220.500100004002.000200006198.500300010020.00'

```

You can install stypes using pip
```bash
pip install stypes
```

or download from PyPI at https://pypi.python.org/pypi/stypes/
