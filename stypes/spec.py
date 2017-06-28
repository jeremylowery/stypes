""" Library for converting python data structures into a field type object
graph. This effectively creates a small domain-specific language for parsing
and writing text files.

The canonical representation for a specification is a list of pairs. Each pair
contains a key name for the type and a type specification.

A brief example:
    [('favorite_color', 5), ('windspeed', 10)]

Is a specification for a record type with 2 fields: favorite_color and
windpseed. favorite_color is a scalar of width 5 and windspeed is a scalar of
width 10.

For such a simple specification, a more terse string version of the
specification might be more appropriate::

  'favorite_color:5;windpseed:10'

There are many shortcuts which make specifications more expressive and
easier to read.

A type specification will be one of the following:

    not given
      If a type specification is not given, it is assumed to be a scalar of
      width 1

    an integer 
      Represents a character scalar value with the given width

    a type object
      An object that implements the Layout protocol

    a list
      A sub-specification

"""
import collections
import string
import re

from util import UnconvertedValue
__all__ = ['SpecificationError', 'spec_from_repr', 'Spec', 'String',
           'MappedString', 'atom_to_scalar', 'atom_to_spec_map',
           'atom_to_spec_seq']

class SpecificationError(Exception):
    pass

class Spec(object):
    """ Abstract base class for all specifications to type check """
    width = 0

    def unpack(self, s):
        """ Given a text string, return a value object for the specification
        """
        return s.rstrip()

    def pack(self, value):
        """ Given a value object, return a text string representation """
        return value[:self.width].ljust(self.width)

class String(Spec):
    def __init__(self, width):
        self.width = width

    def to_bytes(self, text):
        if text is None:
            return self.width * " "
        else:
            return text

class BoxedString(Spec):
    def __init__(self, size, count, sep='\r\n'):
        self.size = size
        self.count = count
        self.width = size * count
        self.sep = sep

    def to_bytes(self, text):
        lines = []
        data = text.split(self.sep)
        for i in range(self.count):
            try:
                line = data[i]
            except IndexError:
                line = ''
            line = line[:self.size].ljust(self.size)
            lines.append(line)
        return "".join(lines)

    def from_bytes(self, text):
        lines = [text[x:x+self.size] for x in range(0,len(text), self.size)]
        return self.sep.join(lines)

class MappedString(Spec):
    def __init__(self, width, smap):
        self._smap = smap
        self.width = width

    def from_bytes(self, text):
        try:
            return self._smap[text]
        except KeyError:
            valid_strings = ', '.join(self._smap.keys())
            return UnconvertedValue(text, 'Expected one of: %s' % valid_strings)


def tokenize_lines(r):
    """ break apart a full string representation into a list. useful for
    mappings and sequences """
    return map(string.strip, r.split(";"))

def atom_to_spec_seq(specs):
    if isinstance(specs, basestring):
        specs = tokenize_lines(specs)
    return map(atom_to_scalar, specs)

_AR_FNAME = re.compile(r"^([A-Za-z0-9_-]+)\S*\[(\d+)\]\S*")
def atom_to_spec_map(rep):
    """ Convert an unknown variable atom into a specficiation map suitable
    for mappings which comprise a list of pairs. Each pairs is of the form:
    (name, spec)
    """
    from .sequence import Array

    key_map = []
    if isinstance(rep, basestring):
        rep = tokenize_lines(rep)
    for key_spec_repr in rep:
        name, spec_atom = _split_key_spec(key_spec_repr)
        
        # Figure out the spec type
        key_spec = atom_to_scalar(spec_atom)

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
    return key_map

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

def spec_from_repr(rep):
    """
    XXX:TODO This isn't used anywhere now. Delete?

    Specifications create field lists and conversion maps for Layout objects
    and convert().

    There is a lot of variability in how a specification can be given. This is
    why it has been encapsulated into a single class.

    Each field can be of the following forms.
    
    "field" | ("field",)
        String size 1
    "field:width" => ("field", width)
        String size "width"
    "field[count]" | (("field", count), 1) 
        Array size 1 with "count" elements
    "field[count]:width"  | (("field", count), width) 
        Array size "width" with "count" elements
    ("field", FieldType())
        Custom Field with size of .width attribute of field
    (("field", count), FieldType)
        Array of Custom Field values with size of field.width * count
    ("field", (fieldspec1, fieldspec2, ...))
        subrecord
    ])

    A complete field representation will be separate fields by commas

    """
    key_map = []
    convert_map = []
    if isinstance(rep, basestring):
        # XXX:TODO Field for subrecords, will have to have a stateful unpackr
        rep = map(string.strip, rep.split(";"))
    for fieldspec in rep:
        name, field = _split_field_layout(fieldspec)
        
        # Figure out the field type
        if isinstance(field, int):
            if field < 1:
                raise SpecificationError("width must be larger than 0 not %r" % field)
            field_type = String(field)
        elif isinstance(field, (list, tuple)):
            # subrecord
            field_type = spec_from_repr(field)
        elif not hasattr(field, "width"):
            raise SpecificationError("Custom field type %r given, but does not "
                "have .width attribute")
        else:
            # We assume they passed in a custom type.
            field_type = field

        # Figure out if an Array def was given to control the field_type
        if isinstance(name, (list, tuple)):
            if len(name) != 2:
                raise SpecificationError("Expected 2 element sequence or "
                    "string for field name, got %r" % name)
            name, count = name
            field_type = Array(count, field_type)
        elif not isinstance(name, basestring):
            raise SpecificationError("Expected 2 element sequence or string "
                "for field name, got %r" % name)

        key_map.append((name, field_type))

        # See if this is a converter to add to the convert map
        if _isconverter(field_type):
            convert_map.append((name, field_type))
    return Dict(key_map, convert_map)

def atom_to_scalar(atom):
    if isinstance(atom, Spec):
        return atom
    elif isinstance(atom, int):
        return String(atom)
    elif isinstance(atom, basestring) and re.match("^\d+$", atom):
        return String(int(atom))
    else:
        raise SpecificationError("Expecting specification, int or object "
                "with width. Got %r" % (atom,))

def _isconverter(obj):
    return hasattr(obj, 'to_bytes') and hasattr(obj, 'from_bytes')

def _split_field_layout(layout):
    if isinstance(layout, basestring):
        if ":" in layout:
            name, width = map(string.strip, layout.split(":", 1))
        else:
            name, width = layout, "1"
    elif isinstance(layout, collections.Sequence):
        if len(layout) > 1:
            name, width = layout[:2]
        elif len(layout) == 1:
            name, width = layout, 1
        else:
            raise SpecificationError("Empty field layout given")
    else:
        raise SpecificationError("Expected sequence or string for field "
            "layout not %r" % layout)

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

