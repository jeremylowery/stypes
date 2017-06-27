import copy
import collections
import re
import struct
import string

from .util import UnconvertedValue
from .spec import Spec, atom_to_spec_map
from .sequence import Array

class _BaseDict(Spec):
    """ Abstract Base Class for Dict Types. Provided only for implementation
    inheritance.  At the time of the writing, the only variation is the type of
    the value class
    """

    _value_type = None

    def __init__(self, key_map=()):
        self._spec_map = atom_to_spec_map(key_map)
        self._unpack_funs = [s.unpack for n, s in self._spec_map]
        self._pack_funs = [s.pack for n, s in self._spec_map]
        self._struct = struct.Struct(self._struct_fmt)
        self._setup_from_str_funs()
        self._setup_to_str_funs()

    @property
    def width(self):
        """ The width of the dictionary record as text """
        return sum(s.width for name, s in self._spec_map)

    ## unpack
    def unpack(self, text_line):
        """ Convert the given byte text into a python mapping """
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
            if hasattr(spec, 'from_bytes'):
                self._from_str_funs.append((idx, spec.from_bytes))

    ## pack
    def pack(self, rec):
        try:
            value = [rec[n] for n, s in self._spec_map]
        except KeyError, e:
            err = "Specification requires value to have a %r key" % e.args
            raise KeyError(err)

        if not self._to_str_funs:
            return ''.join(s(v) for s, v in zip(self._pack_funs, value))

        for idx, to_str in self._to_str_funs:
            value[idx] = to_str(value[idx])
            if isinstance(value[idx], UnconvertedValue):
                return value[idx]

        return ''.join(s(v) for s, v in zip(self._pack_funs, value))

    def _setup_to_str_funs(self):
        # Functions to call when we convert from a value to a string
        self._to_str_funs = []
        for idx, (name, spec) in enumerate(self._spec_map):
            if hasattr(spec, 'to_bytes'):
                self._to_str_funs.append((idx, spec.to_bytes))

    ## Private
    @property
    def _keys(self):
        return [name for name, f in self._spec_map]

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % f.width for name, f in self._spec_map)

class _UnconvertedMappingValueMixIn(object):
    def has_unconverted(self):
        return any(isinstance(s, UnconvertedValue) for s in self.values())

    def unconverted_report(self):
        """ Debugging report that shows all of the values in the mapping
        which were unable to be converted. """
        lines = []
        for key, value in self.items():
            if not isinstance(value, UnconvertedValue):
                continue
            lines.append("Field %s - %s" % (key, value))
        return "\n".join(lines)

class DictValue(dict, _UnconvertedMappingValueMixIn):
    def __init__(self, values, spec):
        dict.__init__(self, values)
        self._spec = spec

    def __copy__(self):
        rec = type(self)(self, self._spec)
        return rec

    def __deepcopy__(self, memo):
        rec = type(self)(self, self._spec)
        return rec

    ## dict protocol
    def __setitem__(self, key, str_value):
        if not isinstance(str_value, basestring):
            return dict.__setitem__(self, key, str_value)
        
        for fun_key, fun in self._spec._from_str_funs:
            if fun_key == key:
                value = fun(str_value)
                break
        else:
            value = str_value
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        raise TypeError("values cannot be removed from stype dicts")

    def clear(self):
        raise TypeError("values cannot be removed from stype dicts")

    def pack(self):
        return self._spec.pack(self)

class Dict(_BaseDict):
    _value_type = DictValue


