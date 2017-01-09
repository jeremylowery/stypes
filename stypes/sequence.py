
import collections
import copy
import re
import string
import struct

from .spec import Spec, atom_to_spec_seq, atom_to_spec_map
from .util import UnconvertedValue

class BaseSequence(Spec):
    _itype = None
    _str_itype = None

    def __init__(self, pos_specs=()):
        self._pos_specs = atom_to_spec_seq(pos_specs)
        self._setup_from_str_funs()
        self._setup_to_str_funs()
        self._unpack_funs = [p.unpack for p in self._pos_specs]
        self._pack_funs = [p.pack for p in self._pos_specs]
        self._struct = struct.Struct(self._struct_fmt)

    @property
    def width(self):
        return sum(s.width for s in self._pos_specs)

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
        return self._itype(values, self)

    def _setup_from_str_funs(self):
        # Functions to call when we convert from a string to a value
        self._from_str_funs = []
        for idx, spec in enumerate(self._pos_specs):
            if hasattr(spec, 'from_bytes'):
                self._from_str_funs.append((idx, spec.from_bytes))

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % s.width for s in self._pos_specs)
        
    ## Pack
    def pack(self, value):
        # Shortcut
        if not self._to_str_funs:
            return ''.join(s(v) for s, v in zip(self._pack_funs, value))

        str_values = list(value)
        for idx, to_str in self._to_str_funs:
            str_values[idx] = to_str(value[idx])
        return ''.join(s(v) for s, v in zip(self._pack_funs, str_values))

    def as_strings(self, value):
        """ Return a builtin NamedTuple that is an 'export' of the value
        into strings
        """
        if not self._to_str_funs:
            return self._str_itype(value)

        str_value = list(value)
        for idx, to_str in self._to_str_funs:
            str_value[idx] = to_str(value[idx])
        return self._str_itype(*str_value)

    def _setup_to_str_funs(self):
        # Functions to call when we convert from a value to a string
        self._to_str_funs = []
        for idx, spec in enumerate(self._pos_specs):
            if hasattr(spec, 'to_bytes'):
                self._to_str_funs.append((idx, spec.to_bytes))

class _UnconvertedSequenceValueMixIn(object):
    def has_unconverted(self):
        return any(isinstance(s, UnconvertedValue) for s in self)

    def unconverted_report(self):
        lines = []
        for idx, value in enumerate(self):
            if not isinstance(value, UnconvertedValue):
                continue
            lines.append("Index %d: %s" % (idx, value))
        return "\n".join(lines)

## NamedTuple
class NamedTuple(BaseSequence):
    def __init__(self, key_map=()):
        self._key_map = atom_to_spec_map(key_map)
        self._field_names = [n for n, c in self._key_map]
        self._str_itype = collections.namedtuple('BaseNamedTuple', self._field_names)
        self._itype = type('NamedTupleValue', (_NamedTupleValue, self._str_itype), {})

        pos_specs = [c for n, c in self._key_map]
        BaseSequence.__init__(self, pos_specs)

class _NamedTupleValue(_UnconvertedSequenceValueMixIn):
    def __new__(cls, value, spec):
        i = cls.__bases__[1].__new__(cls, *value)
        i._spec = spec
        return i

    def pack(self):
        return self._spec.pack(self)

    def as_strings(self):
        return self._spec.as_strings(self)

## Tuple
class Tuple(BaseSequence):
    def __init__(self, *a, **k):
        self._itype = _TupleValue
        self._str_itype = tuple
        BaseSequence.__init__(self, *a, **k)

class _TupleValue(tuple, _UnconvertedSequenceValueMixIn):
    def __new__(cls, other, spec, convert_errors=None):
        inst = tuple.__new__(cls, other)
        inst._spec = spec
        inst._convert_errors = convert_errors or []
        return inst

    def __init__(self, other, spec, convert_errors=None):
        tuple.__init__(self, other)

    def __copy__(self):
        rec = _TupleValue(self, self._spec)
        rec._convert_errors = list(self._convert_errors)
        return rec

    def __deepcopy__(self, memo):
        rec = _TupleValue(self, self._spec)
        rec._convert_errors = copy.deepcopy(self._convert_errors, memo)
        return rec

    def convert_errors(self):
        return list(self._convert_errors)

    def pack(self):
        return self._spec.pack(self)

## List
class List(BaseSequence):
    def __init__(self, *a, **k):
        self._str_itype = list
        self._itype = _ListValue
        BaseSequence.__init__(self, *a, **k)

class Array(List):
    def __init__(self, count, spec):
        self._str_itype = list
        self._itype = _ListValue
        self._count = count
        self._pos_specs = [spec] * count
        self._setup_from_str_funs()
        self._setup_to_str_funs()
        self._unpack_funs = [p.unpack for p in self._pos_specs]
        self._pack_funs = [p.pack for p in self._pos_specs]
        self._struct = struct.Struct(self._struct_fmt)

class _ListValue(list, _UnconvertedSequenceValueMixIn):
    def __init__(self, other, spec):
        list.__init__(self, other)
        self._spec = spec

    def __copy__(self):
        rec = type(self)(self, self._spec)
        return rec

    def __deepcopy__(self, memo):
        rec = type(self)(self, self._spec)
        return rec

    ## List Protocol
    def __setslice__(self, start, end, sublist):
        start, end = max(start, 0), max(end, 0)
        if end > len(self):
            # Possibly a [:] or [idx:] slice
            if len(sublist) != len(self) - start:
                raise TypeError('Cannot change size of list with slice')
            end = len(self) + 1
        for idx, item in zip(range(start, end), sublist):
            self.__setitem__(idx, item)

    def __setitem__(self, index, values):
        if isinstance(index, slice):
            indexes = range(*index.indices(len(self)))
            if len(values) != len(indexes):
                raise TypeError('Cannot change size of list with slice')
        else:
            indexes = [index]
            values = [values]
        
        for index, str_value in zip(indexes, values):
            for fun_index, fun in self._spec._from_str_funs:
                if fun_index == index:
                    value = fun(str_value)
                    break
            else:
                value = str_value
            list.__setitem__(self, index, value)

    def __delitem__(self, index):
        raise TypeError("stype lists cannot change size")

    def __delslice__(self, index):
        raise TypeError("stype lists cannot change size")

    def append(self, value):
        raise TypeError("stype lists cannot change size")

    def extend(self, other):
        raise TypeError("stype lists cannot change size")

    def insert(self, index, value):
        raise TypeError("stype lists cannot change size")

    def pop(self, index=-1):
        raise TypeError("stype lists cannot change size")

    def remove(self, index, value):
        raise TypeError("stype lists cannot change size")

    def reverse(self):
        raise TypeError("Operation not supported")

    ## stypes Protocol
    def pack(self):
        return self._spec.pack(self)

