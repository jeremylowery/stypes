
__all__ = ['unpack', 'pack', 'from_text', 'to_text', 'spec', 'Integer',
           'String', 'Record', 'Array', 'List', 'Tuple', 'UnconvertedValue',
           'NamedTuple', 'SpecificationError', 'NumericFormatError', 'Numeric']

from .date import Date, Datetime
from .mapping import Dict
try:
    from .odict import OrderedDict
except ImportError:
    pass
from .numeric import Integer, Numeric, NumericFormatError
from .sequence import Array, List, Tuple, NamedTuple
from .spec import SpecificationError, String, Spec, MappedString
from .util import UnconvertedValue

## Layout Entry Points
def unpack(string, spec):
    """ Parse a string of text into a record using the given spec"""
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.unpack(string)

def pack(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.pack(rec)

