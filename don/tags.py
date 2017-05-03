import collections

VOID = 0x00
TRUE = 0x01
FALSE = 0x02
BOOL = (TRUE, FALSE)
INT8 = 0x10
INT16 = 0x11
INT32 = 0x12
INT64 = 0x13
# These are to be supported in the future
# FLOAT = 0x20
# DOUBLE = 0x21
BINARY = 0x30
UTF8 = 0x31
UTF16 = 0x32
UTF32 = 0x33
LIST = 0x40
DICTIONARY = 0x41

STRING_TAGS = set([UTF8, UTF16, UTF32])

DEFAULT_INTEGER_ENCODING = INT32
DEFAULT_STRING_ENCODING = UTF8

TaggedObject = collections.namedtuple('TaggedObject', ['tag', 'value'])

_TYPES_TO_TAGS = {
    int: DEFAULT_INTEGER_ENCODING,
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

_NONE = TaggedObject(tag = VOID, value = None)
_TRUE = TaggedObject(tag = TRUE, value = True)
_FALSE = TaggedObject(tag = FALSE, value = False)

_TAGS_TO_IN_RANGE_PREDICATES = collections.OrderedDict([
    (INT8,  lambda i: -128 <= i and i <= 127),
    (INT16, lambda i: -32768 <= i and i <= 32767),
    (INT32, lambda i: -2147483648 <= i and i <= 2147483647),
    (INT64, lambda i: -9223372036854775808 <= i and i <= 9223372036854775807),
])

class TooWideError(Exception):
    pass

SMALLEST = object()

def autotag(o, **kwargs):
    preferred_integer_tag = kwargs.pop('preferred_integer_tag', DEFAULT_INTEGER_ENCODING)
    preferred_string_tag = kwargs.pop('preferred_string_tag', DEFAULT_STRING_ENCODING)

    if kwargs:
        raise TypeError("autotag() got an unexpected keyword argument '{}'".format(
            list(kwargs.keys())[0],
        ))

    if isinstance(o, TaggedObject):
        return o

    if o is None:
        return _NONE

    if o is True:
        return _TRUE

    if o is False:
        return _FALSE

    if isinstance(o, int):
        if preferred_integer_tag is not SMALLEST and _TAGS_TO_IN_RANGE_PREDICATES[preferred_integer_tag](o):
            return TaggedObject(tag = preferred_integer_tag, value = o)

        else:
            for tag, in_range_predicate in _TAGS_TO_IN_RANGE_PREDICATES.items():
                if in_range_predicate(o):
                    return TaggedObject(tag = tag, value = o)

            raise TooWideError("Integer {} is too wide to be serialized")

    if isinstance(o, str):
        # TODO Support SMALLEST for preferred string tag
        return TaggedObject(tag = preferred_string_tag, value = o)

    if isinstance(o, bytes):
        return TaggedObject(tag = BINARY, value = o)

    if isinstance(o, list):
        return TaggedObject(
            tag = LIST,
            value = [
                autotag(
                    i,
                    preferred_integer_tag = preferred_integer_tag,
                    preferred_string_tag = preferred_string_tag,
                ) for i in o
            ],
        )

    if isinstance(o, dict):
        return TaggedObject(
            tag = DICTIONARY,
            value = collections.OrderedDict([
                (
                    autotag(
                        key,
                        preferred_integer_tag = preferred_integer_tag,
                        preferred_string_tag = preferred_string_tag,
                    ),
                    autotag(
                        value,
                        preferred_integer_tag = preferred_integer_tag,
                        preferred_string_tag = preferred_string_tag,
                    ),
                ) for key, value in o.items()
            ]),
        )

    raise Exception('Unsupported type {}'.format(type(o)))
