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

__all__ = ['SpecificationError', 'spec_from_repr', 'Spec', 'Scalar', 'isconverter']

def isconverter(obj):
    return hasattr(obj, 'to_text') and hasattr(obj, 'from_text')

class SpecificationError(Exception):
    pass

class Spec(object):
    """ Abstract base class for all specifications to type check """
    pass

class Scalar(Spec):
    def __init__(self, width):
        self.width = width

def tokenize_lines(r):
    """ break apart a full string representation into a list. useful for
    mappings and sequences """
    return map(string.strip, r.split(";"))

def spec_from_repr(rep):
    """
    Specifications create field lists and conversion maps for Layout objects
    and convert().

    There is a lot of variability in how a specification can be given. This is
    why it has been encapsulated into a single class.

    Each field can be of the following forms.
    
    "field" | ("field",)
        Scalar size 1
    "field:width" => ("field", width)
        Scalar size "width"
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
            field_type = Scalar(field)
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

def atom_to_spec(atom):
    if isinstance(atom, Spec):
        return atom
    elif isinstance(atom, int):
        return Scalar(atom)
    elif hasattr(atom, 'width'):
        return atom
    elif isinstance(atom, basestring) and re.match("^\d+$", atom):
        return Scalar(int(atom))
    else:
        raise SpecificationError("Expecting specification, int or object "
                "with width. Got %r" % atom)

def _isconverter(obj):
    return hasattr(obj, 'to_text') and hasattr(obj, 'from_text')

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

