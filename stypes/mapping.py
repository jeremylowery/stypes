import copy
import collections
import re
import struct
import string

from .util import OrderedDict as _OrderedDict, ConvertError
from .spec import Spec, Scalar, SpecificationError, tokenize_lines, atom_to_spec, isconverter
from .sequence import Array

class _BaseDict(Spec):
    """ Abstract Base Class for Dict Types. Provided only for implementation inheritance.
    At the time of the writing, the only difference is the type of the value class
    """

    _value_type = None

    def __init__(self, key_map=()):
        self._key_map, self._convert_map = _norm_mapping_key_spec(key_map)

        # We inspect the positional specs in the key map to determine which
        # ones have their own parsing routine. If they do not, then we treat 
        # them as a simple string and strip the trailing white space
        self._unpack_funs = []
        for idx, (name, spec)  in enumerate(self._key_map):
            if hasattr(spec, 'unpack'):
                self._unpack_funs.append(spec.unpack)
            else:
                self._unpack_funs.append(string.rstrip)

        # Use the built-in structs module to do the actual string split in C
        self._struct = struct.Struct(self._struct_fmt)

    ## Layout Responsibility
    @property
    def width(self):
        return sum(t.width for name, t in self._key_map)

    def unpack(self, text_line):
        try:
            values = self._struct.unpack_from(text_line)
        except struct.error:
            # pad the line out so that struct will take it
            values = self._struct.unpack_from(text_line.ljust(self.width))

        values = [s(v) for s, v in zip(self._unpack_funs, values)]
        return self._value_type(zip(self._keys, values), self)

    def pack(self, rec):
        parts = []
        for name, ftype in self._key_map:
            value = rec[name]
            if hasattr(ftype, 'pack'):
                value = ftype.pack(value)
            if len(value) > ftype.width:
                value = value[:ftype.width]
            elif len(value) < ftype.width:
                value = value.ljust(ftype.width)
            parts.append(value)
        return ''.join(parts)

    ## Converter Responsibility
    def from_text(self, rec):
        nrec = copy.deepcopy(rec)
        for name, converter in self._convert_map:
            try:
                nrec[name] = converter.from_text(nrec[name])
            except ConvertError, e:
                nrec.add_convert_error(name, nrec[name], e)
        return nrec

    def to_text(self, rec):
        nrec = copy.deepcopy(rec)
        for name, converter in self._convert_map:
            nrec[name] = converter.to_text(nrec[name])
        return nrec

    ## Private
    @property
    def _keys(self):
        return [name for name, f in self._key_map]

    @property
    def _struct_fmt(self):
        return ''.join('%ds' % f.width for name, f in self._key_map)

class DictValue(dict):
    def __init__(self, values, field_type):
        dict.__init__(self, values)
        self._spec = field_type
        self._convert_errors = []

    def __copy__(self):
        rec = type(self)(self, self._spec)
        rec._convert_errors = list(self._convert_errors)
        return rec

    def __deepcopy__(self, memo):
        rec = type(self)(self, self._spec)
        rec._convert_errors = copy.deepcopy(self._convert_errors, memo)
        return rec

    def add_convert_error(self, name, value, error):
        self._convert_errors.append((name, value, error))

    def convert_errors(self):
        return list(self._convert_errors)

    ## Delegators to the field type. It gets everything but unpack because
    ## unpack is used to create a DictValue
    def pack(self):
        return self._spec.pack(self)

    def to_text(self):
        return self._spec.to_text(self)

    def from_text(self):
        return self._spec.from_text(self)

class Dict(_BaseDict):
    _value_type = DictValue

class OrderedDictValue(_OrderedDict):
    def __init__(self, values, field_type):
        _OrderedDict.__init__(self, values)
        self._spec = field_type
        self._convert_errors = []

    def __copy__(self):
        rec = OrderedDictValue(self, self._spec)
        rec._convert_errors = self._convert_errors
        return rec

    def __deepcopy__(self, memo):
        rec = OrderedDictValue(self, self._spec)
        rec._convert_errors = copy.deepcopy(self._convert_errors, memo)
        return rec

    def add_convert_error(self, name, value, error):
        self._convert_errors.append((name, value, error))

    def convert_errors(self):
        return list(self._convert_errors)

    ## Delegators to the field type. It gets everything but unpack because
    ## unpack is used to create a DictValue
    def pack(self):
        return self._spec.pack(self)

    def from_text(self):
        return self._spec.from_text(self)

    def to_text(self):
        return self._spec.to_text(self)

class OrderedDict(_BaseDict):
    _value_type = OrderedDictValue

_AR_FNAME = re.compile(r"^([A-Za-z0-9_-]+)\S*\[(\d+)\]\S*")
def _norm_mapping_key_spec(rep):
    key_map = []
    convert_map = []
    if isinstance(rep, basestring):
        rep = tokenize_lines(rep)
    for key_spec_repr in rep:
        name, spec_atom = _split_key_spec(key_spec_repr)
        
        # Figure out the spec type
        key_spec = atom_to_spec(spec_atom)

        # Figure out if an Array def was given to control the key_spec_type
        if isinstance(name, (list, tuple)):
            if len(name) != 2:
                raise SpecificationError("Expected 2 element sequence or "
                    "string for key_spec name, got %r" % name)
            name, count = name
            key_spec = Array(count, key_spec)
        elif not isinstance(name, basestring):
            raise SpecificationError("Expected 2 element sequence or string "
                "for key_spec name, got %r" % name)

        key_map.append((name, key_spec))

        # See if this is a converter to add to the convert map
        if isconverter(key_spec):
            convert_map.append((name, key_spec))
    return key_map, convert_map

def _split_key_spec(spec):
    if isinstance(spec, basestring):
        if ":" in spec:
            name, width = map(string.strip, spec.split(":", 1))
        else:
            name, width = spec, "1"
    elif isinstance(spec, collections.Sequence):
        if len(spec) > 1:
            name, width = spec[:2]
        elif len(spec) == 1:
            name, width = spec, 1
        else:
            raise SpecificationError("Empty field spec given")
    else:
        raise SpecificationError("Expected sequence or string for field "
            "spec not %r" % spec)

    if isinstance(name, basestring):
        array_match = _AR_FNAME.findall(name)
        if array_match:
            name = (array_match[0][0], int(array_match[0][1]))
        
    if isinstance(width, basestring):
        try:
            width = int(width)
        except ValueError:
            raise SpecificationError("Only width integers are supported "
                "at this time for field types. To use a custom field type "
                "use a tuple. Found %r" % width)

    return name, width


