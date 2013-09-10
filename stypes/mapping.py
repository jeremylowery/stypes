import copy
import collections
import re
import struct
import string

from .util import OrderedDict as _OrderedDict, ConvertError
from .spec import Spec, atom_to_spec_map
from .sequence import Array

class _BaseDict(Spec):
    """ Abstract Base Class for Dict Types. Provided only for implementation inheritance.
    At the time of the writing, the only variation is the type of the value class
    """

    _value_type = None

    def __init__(self, key_map=()):
        self._spec_map = atom_to_spec_map(key_map)
        self._unpack_funs = [s.unpack for n, s in self._spec_map]
        self._pack_funs = [s.pack for n, s in self._spec_map]
        self._struct = struct.Struct(self._struct_fmt)
        self._setup_from_str_funs()
        self._setup_to_str_funs()

    ## Layout Responsibility
    @property
    def width(self):
        return sum(s.width for name, s in self._spec_map)

    ## unpack
    def unpack(self, text_line):
        try:
            values = self._struct.unpack_from(text_line)
        except struct.error:
            # pad the line out so that struct will take it
            values = self._struct.unpack_from(text_line.ljust(self.width))

        values = [s(v) for s, v in zip(self._unpack_funs, values)]

        for idx, from_str in self._from_str_funs:
            values[idx] = from_str(values[idx])

        return self._value_type(zip(self._keys, values), self)

    def _setup_from_str_funs(self):
        # Functions to call when we convert from a string to a value
        self._from_str_funs = []
        for idx, (name, spec) in enumerate(self._spec_map):
            if hasattr(spec, 'from_text'):
                self._from_str_funs.append((idx, spec.from_text))

    ## pack
    def pack(self, rec):
        value = [rec.get(n, None) for n, s in self._spec_map]
        if not self._to_str_funs:
            return ''.join(s(v) for s, v in zip(self._pack_funs, value))

        for idx, to_str in self._to_str_funs:
            str_values[idx] = to_str(value[idx])
        return ''.join(s(v) for s, v in zip(self._pack_funs, str_values))

    def _setup_to_str_funs(self):
        # Functions to call when we convert from a value to a string
        self._to_str_funs = []
        for idx, (name, spec) in enumerate(self._spec_map):
            if hasattr(spec, 'to_text'):
                self._to_str_funs.append((idx, spec.to_text))

    ## Private
    @property
    def _keys(self):
        return [name for name, f in self._spec_map]

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % f.width for name, f in self._spec_map)

class DictValue(dict):
    def __init__(self, values, spec):
        dict.__init__(self, values)
        self._spec = spec

    def __copy__(self):
        rec = type(self)(self, self._spec)
        return rec

    def __deepcopy__(self, memo):
        rec = type(self)(self, self._spec)
        return rec

    def pack(self):
        return self._spec.pack(self)

class Dict(_BaseDict):
    _value_type = DictValue

class OrderedDictValue(_OrderedDict):
    def __init__(self, values, spec):
        _OrderedDict.__init__(self, values)
        self._spec = spec

    def __copy__(self):
        rec = OrderedDictValue(self, self._spec)
        return rec

    def __deepcopy__(self, memo):
        rec = OrderedDictValue(self, self._spec)
        return rec

    ## Delegators to the field type. It gets everything but unpack because
    ## unpack is used to create a DictValue
    def pack(self):
        return self._spec.pack(self)

class OrderedDict(_BaseDict):
    _value_type = OrderedDictValue

