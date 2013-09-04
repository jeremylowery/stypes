Rich Type Library for Textual Data
==================================

stypes is a text parsing, conversion and formatting library written to
efficiently handle large fixed-width text record data files. Convert text
streams into dictionaries, lists, tuples, named tuples, ordered dictionaries
and more using text layout specifications written in 100% pure python.

A simple example of turning some text into a list:

```python

from stypes import List
spec = List([1, 1, 1, 10])
text = "YYNJohnson"
assert List.unpack(text) == ["Y", "Y", "N", "Johnson"]
```


