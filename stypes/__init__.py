
__all__ = ['parse', 'format', 'from_text', 'to_text', 'spec', 'Integer',
           'Scalar', 'Record', 'Array', 'List', 'Tuple', 'ConvertError',
           'NamedTuple', 'SpecificationError', 'NumericFormatError', 'Numeric']

from .mapping import Dict, OrderedDict
from .sequence import Array, List, Tuple, NamedTuple
from .numeric import Integer, Numeric, NumericFormatError
from .spec import SpecificationError, Scalar, Spec
from .util import ConvertError

## High-level Idiomatic API
def expand(self, string, spec):
    """ turn the line of text into a typed record """
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    value = spec.parse(string)
    return spec.convert(value)

## Layout Entry Points
def parse(string, spec):
    """ Parse a string of text into a record using the given spec"""
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.parse(string)

def format(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.format(rec)

## Conversion Entry Points
def from_text(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.from_text(rec)

def to_text(rec, spec):
    if not isinstance(spec, Spec):
        spec = Dict(spec)
    return spec.to_text(rec)

