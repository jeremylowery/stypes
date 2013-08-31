
import collections
import copy
import functools
import re
import string
import struct

from .spec import Spec, tokenize_lines, Scalar, atom_to_spec, isconverter
from .util import OrderedDict, ConvertError

class NamedTuple(Spec):
    @property
    def width(self):
        return sum(s.width for s in self._pos_specs)

    def __init__(self, key_map=()):
        from .mapping import _norm_mapping_key_spec
        self._key_map, cm = _norm_mapping_key_spec(key_map)
        self._field_names = [n for n, c in self._key_map]

        self._pos_converts = []
        for name, spec in self._key_map:
            if isconverter(spec):
                self._pos_converts.append(spec)
            else:
                self._pos_converts.append(None)
        if not any(self._pos_converts):
            self._pos_converts = None

        nt_class = collections.namedtuple('BaseNamedTuple', self._field_names)
        self._my_class = type('NamedTuple', (_NamedTupleValue, nt_class), {})

        # We inspect the positional specs in the key map to determine which
        # ones have their own parsing routine. If they do not, then we treat 
        # them as a simple string and strip the trailing white space
        self._sub_parses = []
        for idx, (name, spec)  in enumerate(self._key_map):
            if hasattr(spec, 'parse'):
                self._sub_parses.append(spec.parse)
            else:
                self._sub_parses.append(string.rstrip)

        # Use the built-in structs module to do the actual string split in C
        self._struct = struct.Struct(self._struct_fmt)

    def parse(self, text_line):
        try:
            values = self._struct.unpack_from(text_line)
        except struct.error:
            # pad the line out so that struct will take it
            values = self._struct.unpack_from(text_line.ljust(self.width))

        values = [s(v) for s, v in zip(self._sub_parses, values)]
        return self._my_class(values, self)

    def from_text(self, avalue):
        if not self._pos_converts:
            return copy.copy(avalue)

        convert_errors = []
        nvalue = []
        for idx, (value, convert) in enumerate(zip(avalue, self._pos_converts)):
            if convert:
                try:
                    nvalue.append(convert.from_text(value))
                except ConvertError, e:
                    nvalue.append(value)
                    convert_errors.append((idx, value, e))
            else:
                nvalue.append(value)
        return self._my_class(nvalue, self, convert_errors)

    def to_text(self, avalue):
        if not self._pos_converts:
            return copy.copy(avalue)

        convert_errors = []
        nvalue = []
        for idx, (value, convert) in enumerate(zip(avalue, self._pos_converts)):
            if convert:
                try:
                    nvalue.append(convert.to_text(value))
                except ConvertError, e:
                    nvalue.append(value)
                    convert_errors.append((idx, value, e))
            else:
                nvalue.append(value)
        return self._my_class(nvalue, self, convert_errors)

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % f.width for name, f in self._key_map)
        
class _NamedTupleValue(object):
    def __new__(cls, value, spec, convert_errors=None):
        i = cls.__bases__[1].__new__(cls, *value)
        i._spec = spec
        i._convert_errors = convert_errors or []
        return i

    def from_text(self):
        return self._spec.from_text(self)

    def to_text(self):
        return self._spec.to_text(self)

class _BaseSequence(Spec):
    _factory = None

    def __init__(self, pos_specs):
        self._pos_specs = _norm_sequence_pos_specs(pos_specs)
        self._pos_converts = []
        for spec in self._pos_specs:
            if isconverter(spec):
                self._pos_converts.append(spec)
            else:
                self._pos_converts.append(None)
        if not any(self._pos_converts):
            self._pos_converts = None

        # We inspect the positional specs in the key map to determine which
        # ones have their own parsing routine. If they do not, then we treat 
        # them as a simple string and strip the trailing white space
        self._sub_parses = []
        for idx, pos_spec  in enumerate(self._pos_specs):
            if hasattr(pos_spec, 'parse'):
                self._sub_parses.append(pos_spec.parse)
            else:
                self._sub_parses.append(string.rstrip)

        # Use the built-in structs module to do the actual string split in C
        self._struct = struct.Struct(self._struct_fmt)

        self._format_funcs = []
        for pos_spec in self._pos_specs:
            if hasattr(pos_spec, 'format'):
                func = pos_spec.format
            elif hasattr(pos_spec, 'width'):
                func = functools.partial(_format_string, pos_spec.width)
            else:
                func = functools.partial(_format_string, pos_spec)
            self._format_funcs.append(func)

    ## Convinenece to do parsing/conversion and conversion/formatting in single
    ## operations
    def expand(self, text_line):
        """ turn the line of text into a typed record """
        return self.from_text(self.parse(text_line))

    def squash(self, rec):
        """ turn the typed record into a line of text """
        return self.format(self.to_text(rec))

    @property
    def width(self):
        return sum(s.width for s in self._pos_specs)

    def parse(self, string):
        try:
            values = self._struct.unpack_from(string)
        except struct.error:
            # pad the line out so that struct will take it
            values = self._struct.unpack_from(string.ljust(self.width))
        v = [s(v) for s, v in zip(self._sub_parses, values)]
        return self._factory(v, self)

    def format(self, listval):
        return ''.join(s(v) for s, v in zip(self._format_funcs, listval))

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % f.width for  f in self._pos_specs)

def _norm_sequence_pos_specs(specs):
    """ Normalize sequence specs passed in from client calls. These can have
    ints, strings, and types in them.
    """
    if isinstance(specs, basestring):
        specs = tokenize_lines(specs)
    return map(atom_to_spec, specs)

class List(_BaseSequence):
    def __init__(self, *a, **k):
        _BaseSequence.__init__(self, *a, **k)
        self._factory = _ListValue

    ## Converter Responsibilities
    def from_text(self, avalue):
        nvalue = copy.deepcopy(avalue)
        if not self._pos_converts:
            return nvalue

        for idx, (value, convert) in enumerate(zip(avalue, self._pos_converts)):
            if convert:
                try:
                    nvalue[idx] = convert.from_text(value)
                except ConvertError, e:
                    convert_errors.append((idx, value, e))
        return nvalue

    def to_text(self, avalue):
        nvalue = copy.deepcopy(avalue)
        if not self._pos_converts:
            return nvalue

        for idx, (value, convert) in enumerate(zip(avalue, self._pos_converts)):
            if convert:
                try:
                    nvalue[idx] = convert.to_text(value)
                except ConvertError, e:
                    convert_errors.append((idx, value, e))
        return nvalue


class _ListValue(list):
    def __init__(self, other, spec):
        list.__init__(self, other)
        self._spec = spec
        self._convert_errors = []

    def __copy__(self):
        rec = _ListValue(self, self._spec)
        rec._convert_errors = list(self._convert_errors)
        return rec

    def __deepcopy__(self, memo):
        rec = _ListValue(self, self._spec)
        rec._convert_errors = copy.deepcopy(self._convert_errors, memo)
        return rec

    def add_convert_error(self, index, value, error):
        self._convert_errors.append((index, value, error))

    def convert_errors(self):
        return list(self._convert_errors)


class Tuple(_BaseSequence):
    def __init__(self, *a, **k):
        _BaseSequence.__init__(self, *a, **k)
        self._factory = _TupleValue

    def from_text(self, avalue):
        if not self._pos_converts:
            return copy.copy(avalue)

        convert_errors = []
        nvalue = []
        for idx, value in enumerate(avalue):
            try:
                conv = self._pos_converts[idx]
            except IndexError:
                nvalue.append(value)
                continue
            try:
                nvalue.append(conv.from_text(value))
            except ConvertError, e:
                nvalue.append(value)
                convert_errors.append((idx, value, e))
        return _TupleValue(nvalue, self, convert_errors)

    def to_text(self, avalue):
        if not self._pos_converts:
            return copy.copy(avalue)

        convert_errors = []
        nvalue = []
        for idx, value in enumerate(avalue):
            try:
                conv = self._pos_converts[idx]
            except IndexError:
                nvalue.append(value)
                continue
            try:
                nvalue.append(conv.to_text(value))
            except ConvertError, e:
                nvalue.append(value)
                convert_errors.append((idx, value, e))
        return _TupleValue(nvalue, self, convert_errors)

class _TupleValue(tuple):
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

class Array(Spec):
    def __init__(self, count, spec):
        self._count = count
        self._spec = atom_to_spec(spec)

        # Do this lookup here to save it from doing in parse
        self._sub_parse = hasattr(spec, 'parse')
        if isconverter(spec):
            self._converter = spec
        else:
            self._converter = None

    @property
    def width(self):
        return self._count * self._spec.width

    ## Layout Responsibilities
    def parse(self, text_line):
        if len(text_line) < self.width:
            # pad the line out so that struct won't blow up
            text_line += ' ' * (self.width - len(text_line))
        parts = map(''.join, zip(*[iter(text_line)] * self._spec.width))
        if self._sub_parse:
            parts = map(self._spec.parse, parts)
        return ArrayValue(parts, self)

    def format(self, avalue):
        parts = []
        field = self._spec
        for value in avalue:
            if hasattr(field, 'format'):
                value = field.format(value)
            if len(value) > field.width:
                value = value[:field.width]
            elif len(value) < field.width:
                value = value.ljust(width)
            parts.append(value)
        return ''.join(parts)

    ## Converter Responsibilities
    def from_text(self, avalue):
        nvalue = copy.deepcopy(avalue)
        if self._converter:
            for idx, value in enumerate(avalue):
                try:
                    nvalue[idx] = self._converter.from_text(value)
                except ConvertError, e:
                    nrec.add_convert_error(idx, value, e)
        return nvalue

    def to_text(self, avalue):
        nvalue = copy.deepcopy(avalue)
        if self._converter:
            for idx, value in enumerate(avalue):
                try:
                    nvalue[idx] = self._converter.to_text(value)
                except ConvertError, e:
                    nrec.add_convert_error(idx, value, e)
        return nvalue

class ArrayValue(list):
    def __init__(self, values, field):
        list.__init__(self, values)
        self._field = field
        self._convert_errors = []

    def __copy__(self):
        rec = ArrayValue(self, self._field)
        rec._convert_errors = self._convert_errors
        return rec

    def __deepcopy__(self, memo):
        rec = ArrayValue(self, self._field)
        rec._convert_errors = copy.deepcopy(self._convert_errors, memo)
        return rec

    def add_convert_error(self, index, value, error):
        self._convert_errors.append((index, value, error))

    def convert_errors(self):
        return list(self._convert_errors)

def _format_string(length, value):
    return value[:length].ljust(length)
