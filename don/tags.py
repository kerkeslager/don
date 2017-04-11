import collections

VOID = 0x00
TRUE = 0x01
FALSE = 0x02
BOOL = (TRUE, FALSE)
INT8 = 0x10
INT16 = 0x11
INT32 = 0x12
INT64 = 0x13
FLOAT = 0x20
DOUBLE = 0x21
BINARY = 0x30
UTF8 = 0x31
UTF16 = 0x32
UTF32 = 0x33
LIST = 0x40
DICTIONARY = 0x41

DEFAULT_INTEGER_ENCODING = INT32
DEFAULT_DECIMAL_ENCODING = DOUBLE
DEFAULT_STRING_ENCODING = UTF8

TaggedObject = collections.namedtuple('TaggedObject', ['tag', 'value'])

_TYPES_TO_TAGS = {
    int: DEFAULT_INTEGER_ENCODING,
    float: DEFAULT_DECIMAL_ENCODING,
    bytes: BINARY,
    str: DEFAULT_STRING_ENCODING,
    list: LIST,
    dict: DICTIONARY,
    collections.OrderedDict: DICTIONARY,
}

def _tag(o):
    if isinstance(o, TaggedObject):
        return o

    if o is None:
        return TaggedObject(tag = VOID, value = o)

    if o is True:
        return TaggedObject(tag = TRUE, value = o)

    if o is False:
        return TaggedObject(tag = FALSE, value = o)

    return TaggedObject(tag = _TYPES_TO_TAGS[type(o)], value = o)
