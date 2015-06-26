Encode and Decode Textual Data into Rich Python Data Structures
===============================================================

stypes is a text parsing, conversion and formatting library written to
efficiently handle large fixed-width text record data files. Convert text
streams into dictionaries, lists, tuples, named tuples, ordered dictionaries
and more using text layout specifications. Nested data structures and
repeating elements are also supported.

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

See the included tests.py file for more examples.

Errors in Data
------------------------------------
stypes takes the approach that errors in the textual data are not exceptions.
Data errors are to be expected and should be handled in the normal flow of the
program.

stypes includes the notion of an UnconvertedValue. When parsing text that cannot be
deserialized into the destination format, an UnconvertedValue instance is placed in
it's place. All container objects have a has_unconverted() method which allows
client code to easily detect if there was an error.

```python
fmt = List([Numeric('99V9'), Integer(4)])
rec = fmt.unpack("44X001A")
print rec
[<UnconvertedValue string='44X' reason="Expected 1 digits. Found 'X'">,
 <UnconvertedValue string='001A' reason='expecting all digits for integer'>]

assert rec.has_unconverted() == True

print rec[0].reason
 "Expected 1 digits. Found 'X'"

print rec[1].reason
 'expecting all digits for integer'
```

Installation
------------------------

You can install stypes using pip
```bash
pip install stypes
```

or download from PyPI at https://pypi.python.org/pypi/stypes/
