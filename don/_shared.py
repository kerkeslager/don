import collections

from don import constants

_TYPES_TO_TAGS = {
    int: constants.DEFAULT_INTEGER_ENCODING,
    float: constants.DEFAULT_DECIMAL_ENCODING,
    bytes: constants.BINARY,
    str: constants.DEFAULT_STRING_ENCODING,
    list: constants.LIST,
    dict: constants.DICTIONARY,
    collections.OrderedDict: constants.DICTIONARY,
}

TaggedObject = collections.namedtuple('TaggedObject', ['tag', 'value'])

def _tag(o):
    if isinstance(o, TaggedObject):
        return o

    if o is None:
        return TaggedObject(tag = constants.VOID, value = o)

    if o is True:
        return TaggedObject(tag = constants.TRUE, value = o)

    if o is False:
        return TaggedObject(tag = constants.FALSE, value = o)

    return TaggedObject(tag = _TYPES_TO_TAGS[type(o)], value = o)

ParseResult = collections.namedtuple(
    'ParseResult',
    [
        'success',
        'value',
        'remaining',
    ],
)

_FAILED_PARSE_RESULT = ParseResult(success = False, value = None, remaining = None)
