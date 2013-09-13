Rich Type Library for Textual Data
==================================

stypes is a text parsing, conversion and formatting library written to
efficiently handle large fixed-width text record data files. Convert text
streams into dictionaries, lists, tuples, named tuples, ordered dictionaries
and more using text layout specifications.

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


