
__all__ = ['unpack', 'pack', 'from_text', 'to_text', 'spec', 'Integer',
           'String', 'Record', 'Array', 'List', 'Tuple', 'UnconvertedValue',
           'NamedTuple', 'SpecificationError', 'NumericFormatError', 'Numeric']

from .mapping import Dict, OrderedDict
from .sequence import Array, List, Tuple, NamedTuple
from .numeric import Integer, Numeric, NumericFormatError
from .spec import SpecificationError, String, Spec
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

## Conversion Entry Points
def from_text(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.from_text(rec)

def to_text(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.to_text(rec)

