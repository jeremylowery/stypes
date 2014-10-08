import datetime
import time
import re

from .spec import Spec
from .util import InvalidSpecError, UnconvertedValue

class Date(Spec):
    def __init__(self, fmt):
        self._fmt = fmt
        self._width = _formatter_width(fmt)

    @property
    def width(self):
        return self._width

    def from_bytes(self, text):
        if not text.strip():
            return None
        try:
            t = time.strptime(text, self._fmt)
        except ValueError:
            return UnconvertedValue(text, 'expected date in format %r' % self._fmt)
            
        return datetime.date(*(t[:3]))

    def to_bytes(self, value):
        if value is None:
            return ' '*self.width
        return value.strftime(self._fmt)

class Datetime(Spec):
    def __init__(self, fmt):
        self._fmt = fmt
        self._width = _formatter_width(fmt)

    @property
    def width(self):
        return self._width

    def from_bytes(self, text):
        if not text.strip():
            return None
        try:
            t = time.strptime(text, self._fmt)
        except ValueError:
            return UnconvertedValue(text, 'expected date in format %r' % self._fmt)
        return datetime.datetime(*(t[:6]))

    def to_bytes(self, value):
        if value is None:
            return ' '*self.width
        return value.strftime(self._fmt)

def _formatter_width(fmt):
    formatters = re.findall("%.", fmt)
    fixed_chars = re.sub("%.", "", fmt)
    try:
        width = sum(_formatter_width_map[x] for x in formatters)
    except KeyError, e:
        raise InvalidSpecError("Invalid formatter %s. Perhaps variable length" % e.args)
    return width + len(fixed_chars)

_formatter_width_map = {
       '%a': 3, # The abbreviated weekday name according to the current locale.
#       '%A': , # The full weekday name according to the current locale. NOT SUPPORTED VARIABLE LENGTH
       '%b': 3, # The abbreviated month name according to the current locale.
#       '%B': , # The full month name according to the current locale. NOT SUPPORTED VARIABLE LENGTH
#       '%c': , # The preferred date and time representation for the current locale. NOT SUPPORTED VARIABLE
       '%C': 2, # The century number (year/100) as a 2-digit integer. (SU)
       '%d': 2, # The day of the month as a decimal number (range 01 to 31).
       '%D': 8, # Equivalent to %m/%d/%y.
       '%e': 2, # Like %d, the day of the month as a decimal number, but a leading zero is replaced by a space. (SU)
       '%F': 10,# Equivalent to %Y-%m-%d (the ISO 8601 date format). (C99)
       '%G': 4, # The ISO 8601 week-based year (see NOTES) with century as a
                # decimal number.  The 4-digit year corresponding to the ISO
                # week number (see %V).  This has the  same  format  and value
                # as %Y, except that if the ISO week number belongs to the
                # previous or next year, that year is used instead. (TZ)
       '%g': 2, # Like %G, but without century, that is, with a 2-digit year (00-99). (TZ)
       '%h': 3, # Equivalent to %b.  (SU)
       '%H': 2, # The hour as a decimal number using a 24-hour clock (range 00 to 23).
       '%I': 2, # The hour as a decimal number using a 12-hour clock (range 01 to 12).
       '%j': 3, # The day of the year as a decimal number (range 001 to 366).
       '%k': 2, # The hour (24-hour clock) as a decimal number (range 0 to 23); single digits are preceded by a blank.  (See also %H.)  (TZ)
       '%l': 2, # The hour (12-hour clock) as a decimal number (range 1 to 12); single digits are preceded by a blank.  (See also %I.)  (TZ)
       '%m': 2, # The month as a decimal number (range 01 to 12).
       '%M': 2, # The minute as a decimal number (range 00 to 59).
#       '%n': , # A newline character. (SU) NOT SUPPORTED DOESNT MAKE SENSE IN TEXTUAL RECORD
#       '%O': , # Modifier: use alternative format, see below. (SU)
       '%p': 2, # Either "AM" or "PM" according to the given time value, or the corresponding strings for the current locale.  Noon is treated as "PM" and midnight as "AM".
       '%P': 2, # Like %p but in lowercase: "am" or "pm" or a corresponding string for the current locale. (GNU)
       '%r':11, # The time in a.m. or p.m. notation.  In the POSIX locale this is equivalent to %I:%M:%S %p.  (SU)
       '%R': 5, # The time in 24-hour notation (%H:%M). (SU) For a version including the seconds, see %T below.
#       '%s': , # The number of seconds since the Epoch, 1970-01-01 00:00:00 +0000 (UTC). (TZ) NOT SUPPORTED VARIABLE LENGTH
       '%S': 2, # The second as a decimal number (range 00 to 60).  (The range is up to 60 to allow for occasional leap seconds.)
       '%t': 1, # A tab character. (SU)
       '%T': 8, # The time in 24-hour notation (%H:%M:%S). (SU)
       '%u': 1, # The day of the week as a decimal, range 1 to 7, Monday being 1.  See also %w.  (SU)
       '%U': 2, # The week number of the current year as a decimal number, range 00 to 53, starting with the first Sunday as the first day of week 01.  See also %V and %W.
       '%V': 2, # The  ISO 8601 week number of the current year as a decimal number, range 01 to 53, where week 1 is the first week that has at least 4 days in the new year.
       '%w': 1, # The day of the week as a decimal, range 0 to 6, Sunday being 0.  See also %u.
       '%W': 2, # The week number of the current year as a decimal number, range 00 to 53, starting with the first Monday as the first day of week 01.
#       '%x': , # The preferred date representation for the current locale without the time. NOT SUPPORTED VARIABLE LENGTH
#       '%X': , # The preferred time representation for the current locale without the date. NOT SUPPORTED VARIABLE LENGTH
       '%y': 2, # The year as a decimal number without a century (range 00 to 99).
       '%Y': 4, # The year as a decimal number including the century.
       '%z': 5, # The +hhmm or -hhmm numeric timezone (that is, the hour and minute offset from UTC). (SU)
       '%Z': 3, # The timezone or name or abbreviation.
       '%%': 1  #     A literal '%' character.
}
