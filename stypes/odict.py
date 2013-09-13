
try:
    from collections import OrderedDict as _OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict as _OrderedDict
    except ImportError:
        raise ImportError("Install ordereddict to access this feature in Python < 2.7")

from .util import UnconvertedValue
from .mapping import _UnconvertedMappingValueMixIn, _BaseDict

class OrderedDictValue(_OrderedDict, _UnconvertedMappingValueMixIn):
    def __init__(self, values, spec):
        self._spec = spec
        _OrderedDict.__init__(self, values)

    def __copy__(self):
        rec = OrderedDictValue(self, self._spec)
        return rec

    def __deepcopy__(self, memo):
        rec = OrderedDictValue(self, self._spec)
        return rec

    def update(self, other):
        for key, value in other.items():
            self.__setitem__(key, value)

    def __setitem__(self, key, str_value):
        if not isinstance(str_value, basestring):
            return _OrderedDict.__setitem__(self, key, str_value)
        
        for fun_key, fun in self._spec._from_str_funs:
            if fun_key == key:
                value = fun(str_value)
                break
        else:
            value = str_value
        _OrderedDict.__setitem__(self, key, value)

    def __delitem__(self, key):
        raise TypeError("values cannot be removed from stype dicts")

    def clear(self):
        raise TypeError("values cannot be removed from stype dicts")

    ## Delegators to the field type. It gets everything but unpack because
    ## unpack is used to create a DictValue
    def pack(self):
        return self._spec.pack(self)

class OrderedDict(_BaseDict):
    _value_type = OrderedDictValue
