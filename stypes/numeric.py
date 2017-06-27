
import decimal
import re

from cStringIO import StringIO

from .spec import Spec
from .util import UnconvertedValue, InvalidSpecError

class Integer(Spec):
    def __init__(self, width, pad='0'):
        self.width = width
        self.pad = pad

    def from_bytes(self, text):
        clean = text.strip()
        if not clean:
            return None
        try:
            return int(text.strip())
        except ValueError:
            return UnconvertedValue(text, 'expecting all digits for integer')

    def to_bytes(self, value):
        if value is None:
            text = ''
        else:
            text = str(value)
        if len(text) > self.width:
            msg = 'Cannot fit into text of width %d' % self.width
            return UnconvertedValue(text, msg)
        elif len(text) < self.width:
            return text.rjust(self.width, self.pad)
        else:
            return text

class NumericFormatError(InvalidSpecError):
    pass

class Numeric(Spec):
    """ 9(6)V99
        999V99
        999.99
        999,999.99
    """

    width = property(lambda s: s._width)

    def __init__(self, fspec):
        self._fspec = fspec
        self._converters = []
        self._build_convert_procs()
        self._compute_precision()
        self._width = sum(c.width for c in self._converters)

    def from_bytes(self, text):
        if not text.strip():
            return None
        if len(text) != self._width:
            text = text.rjust(self._width)
        text_input = StringIO(text)
        decimal_input = ConvertState()
        for converter in self._converters:
            err = converter.write_decimal_input(text_input, decimal_input)
            if err:
                return UnconvertedValue(text, err)
        try:
            v = decimal.Decimal(decimal_input.getvalue())
            return v if decimal_input.positive else -v
        except decimal.InvalidOperation, e:
            return UnconvertedValue(text, err)

    def to_bytes(self, value):
        if value is None:
            return ' '*self._width
        text = self._precision_fmt % abs(value)
        buf = ConvertState(text[::-1])
        if value < 0:
            buf.positive = False
        out = StringIO()

        #print self._fspec, value, buf.getvalue(), self._precision_fmt, list(reversed(self._converters))
        for converter in reversed(self._converters):
            err = converter.write_output_text(buf, out)
            if err:
                return UnconvertedValue(text, err)
        return out.getvalue()[::-1]

    def _compute_precision(self):
        """ The precision of the numeric value. We have to have this so when
        we write the data out to text it will pad out correctly """
        prec = 0
        adding = False
        for c in self._converters:
            # find a decimal point
            if isinstance(c, (VConverter, DECIMALConverter)):
                adding = True
            elif isinstance(c, (VConverter, SIGNConverter)):
                pass
            # add all the numbers past it
            elif adding:
                prec += c.width
        self._precision_fmt = "%." + str(prec) + "f"

    def _build_convert_procs(self):
        nine_count = 0
        paren_digits = ''
        symbols = list(self._fspec)
        state = 'START'
        has_sign = False
        DIGIT = re.compile("\d")
        for position, symbol in enumerate(self._fspec):
            position += 1
            if state == 'START':
                if symbol == '9':
                    state = 'NINE'
                    nine_count = 1
                elif symbol == '.':
                    self._converters.append(DECIMALConverter())
                elif symbol == ',':
                    self._converters.append(COMMAConverter())
                elif symbol == 'V':
                    self._converters.append(VConverter())
                elif symbol == 'S':
                    if has_sign:
                        raise NumericFormatError("Unexpected sign at "
                            "position %s. Only one S allowed." % position)
                    has_sign = True
                    self._converters.append(SIGNConverter())
                elif symbol == ' ':
                    self._converters.append(SPACEConverter())
                else:
                    raise NumericFormatError("Unexpected character %r at "
                        "position %s" % (symbol, position))
            elif state == 'NINE':
                if symbol == '9':
                    nine_count += 1
                elif symbol == '.':
                    self._converters.append(NINEConverter(nine_count))
                    self._converters.append(DECIMALConverter())
                    nine_count = 0
                    state = 'START'
                elif symbol == ',':
                    self._converters.append(NINEConverter(nine_count))
                    self._converters.append(COMMAConverter())
                    nine_count = 0
                    state = 'START'
                elif symbol == 'V':
                    self._converters.append(NINEConverter(nine_count))
                    self._converters.append(VConverter())
                    nine_count = 0
                    state = 'START'
                elif symbol == 'S':
                    if has_sign:
                        raise NumericFormatError("Unexpected sign at "
                            "position %s. Only one S allowed." % position)
                    has_sign = True
                    self._converters.append(NINEConverter(nine_count))
                    self._converters.append(SIGNConverter())
                    nine_count = 0
                    state = 'START'
                elif symbol == '(':
                    state = 'LPAREN'
                else:
                    raise NumericFormatError("Unexpected character %r at "
                        "position %s" % (symbol, position))
            elif state == 'LPAREN':
                if DIGIT.match(symbol):
                    paren_digits += symbol
                elif symbol == ')':
                    # We have a -1 here because we got the first 9 of the
                    # paren on the 9 preciding
                    if paren_digits:            # Weird case of 9()
                        pd = int(paren_digits)
                        if pd != 0:             # Weird case of 9(0)
                            nine_count += int(paren_digits) - 1
                    paren_digits = ''
                    state = 'NINE'
                else:
                    raise NumericFormatError("Unexpected character %r at "
                        "position %s" % (symbol, position))
        if state == 'NINE':
            self._converters.append(NINEConverter(nine_count))
        elif state == 'LPAREN':
            raise NumericFormatError("Unexpected end of input. expected )")

class ConvertState(object):
    """ We need a stateful object to keep track of whether the number is
    positive or negative. If we could, we we've just added an attribute to the
    StringIO buffer.
    """
    def __init__(self, iv=None):
        if iv is None:
            self.buf = StringIO()
        else:
            self.buf = StringIO(iv)
        self.positive = True
    def read(self, n):
        return self.buf.read(n)
    def write(self, v):
        self.buf.write(v)
    def getvalue(self):
        return self.buf.getvalue()

class VConverter(object):
    width = property(lambda s: 0)

    def __repr__(self):
        return "V"

    def write_decimal_input(self, inp, outp):
        outp.write(".")

    def write_output_text(self, inp, outp):
        v = inp.read(1)
        if v != ".":
            return "Excepted '.' found %r" % v

class SIGNConverter(object):
    width = property(lambda s: 1)

    def __repr__(self):
        return "S"

    def write_decimal_input(self, inp, outp):
        v = inp.read(1)
        if v == "-":
            outp.positive = False
        else:
            outp.positive = True

    def write_output_text(self, inp, outp):
        if inp.positive:
            outp.write(" ")
        else:
            outp.write("-")

class DECIMALConverter(object):
    width = property(lambda s: 1)

    def __repr__(self):
        return "."

    def write_decimal_input(self, inp, outp):
        v = inp.read(1)
        if v != ".":
            return "Excepted '.' found %r" % v
        outp.write(".")

    def write_output_text(self, inp, outp):
        v = inp.read(1)
        if v != ".":
            return "Excepted '.' found %r" % v
        outp.write(".")

class COMMAConverter(object):
    width = property(lambda s: 1)

    def __repr__(self):
        return ","

    def write_decimal_input(self, inp, outp):
        v = inp.read(1)
        if v != ",":
            return "Excepted ',' found %r" % v

    def write_output_text(self, inp, outp):
        outp.write(",")

class SPACEConverter(object):
    def __repr__(self):
        return "_"

    width = property(lambda s: 1)
    def write_decimal_input(self, inp, outp):
        """ We ignore whatever is in the input on a space """
        inp.read(1)

    def write_output_text(self, inp, outp):
        outp.write(" ")

class NINEConverter(object):
    width = property(lambda s: s._count)

    def __init__(self, count):
        self._count = count
        self._matcher = re.compile("[ \d]{%s}" % count)

    def __repr__(self):
        return "9(%d)" % self.width

    def write_decimal_input(self, inp, outp):
        inv = inp.read(self._count)
        if not self._matcher.match(inv):
            return "Expected %s digits. Found %r" % (self._count, inv)
        outp.write(inv.replace(" ", "0"))

    def write_output_text(self, inp, outp):
        # change "00.25" into "00025" with
        # "00.20" into "00020"
        # 9(3),V,9(2)
        # need to process this backwards
        bytes = inp.read(self.width)
        if not re.match("^\d*$", bytes):
            return "Found non numeric data %r in value" % bytes
        if len(bytes) != self.width:
            bytes = bytes.ljust(self.width, "0")
        outp.write(bytes)

