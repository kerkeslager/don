import binascii
import collections
import functools
import re

from don import tags, _shared

def _integer_size_to_string_serializer(integer_size):
    minimum = -(2 ** (integer_size - 1))
    maximum = 2 ** (integer_size - 1) - 1
    
    def serializer(integer):
        assert minimum <= integer and integer <= maximum
        return '{}i{}'.format(integer, integer_size)

    return serializer

def _serialize_float(f):
    return '{}f'.format(f)

def _serialize_double(d):
    return '{}d'.format(d)

def _serialize_binary(b):
    return '"{}"b'.format(binascii.hexlify(b).decode('ascii'))

def _utf_encoding_to_serializer(utf_encoding):
    def serializer(s):
        return '"{}"{}'.format(s, utf_encoding)

    return serializer

def _string_serialize_list(l):
    return '[{}]'.format(', '.join(map(serialize, l)))

def _string_serialize_dictionary(d):
    def serialize_kvp(kvp):
        return serialize(kvp[0]) + ': ' + serialize(kvp[1])
    return '{ ' + ', '.join(map(serialize_kvp, d.items())) + ' }'

_STRING_SERIALIZERS = {
    tags.VOID: lambda o: 'null',
    tags.TRUE: lambda o: 'true',
    tags.FALSE: lambda o: 'false',
    tags.INT8: _integer_size_to_string_serializer(8),
    tags.INT16: _integer_size_to_string_serializer(16),
    tags.INT32: _integer_size_to_string_serializer(32),
    tags.INT64: _integer_size_to_string_serializer(64),
    tags.FLOAT: _serialize_float,
    tags.DOUBLE: _serialize_double,
    tags.BINARY: _serialize_binary,
    tags.UTF8: _utf_encoding_to_serializer('utf8'),
    tags.UTF16: _utf_encoding_to_serializer('utf16'),
    tags.UTF32: _utf_encoding_to_serializer('utf32'),
    tags.LIST: _string_serialize_list,
    tags.DICTIONARY: _string_serialize_dictionary,
}

def serialize(o):
    o = tags.autotag(o)
    
    return _STRING_SERIALIZERS[o.tag](o.value)

def _consume_leading_whitespace(wrapped_parser):
    @functools.wraps(wrapped_parser)
    def parser(s):
        s = s.lstrip()
        return wrapped_parser(s)

    return parser

def _make_constant_parser(constant, value):
    @_consume_leading_whitespace
    def constant_parser(s):
        if s.startswith(constant):
            result = _shared.ParseResult(
                success = True,
                value = value,
                remaining = s[len(constant):],
            )
            return result

        return _shared._FAILED_PARSE_RESULT

    return constant_parser

def _make_integer_parser(width):
    matcher = re.compile(r'(-?\d+)i' + str(width))

    @_consume_leading_whitespace
    def integer_parser(s):
        match = matcher.match(s)

        if match:
            # TODO Validate that the integer is in range
            return _shared.ParseResult(
                success = True,
                value = int(match.group(1)),
                remaining = s[match.end():],
            )

        return _shared._FAILED_PARSE_RESULT

    return integer_parser

_BINARY32_MATCHER = re.compile(r'(-?\d+\.\d+)f')
_BINARY64_MATCHER = re.compile(r'(-?\d+\.\d+)d')

@_consume_leading_whitespace
def _binary32_parser(s):
    match = _BINARY32_MATCHER.match(s)

    if match:
        # TODO Validate that the float is in range
        return _shared.ParseResult(
            success = True,
            value = float(match.group(1)),
            remaining = s[match.end():],
        )

    return _shared._FAILED_PARSE_RESULT

@_consume_leading_whitespace
def _binary64_parser(s):
    match = _BINARY64_MATCHER.match(s)

    if match:
        # TODO Validate that the double is in range
        return _shared.ParseResult(
            success = True,
            value = float(match.group(1)),
            remaining = s[match.end():],
        )

    return _shared._FAILED_PARSE_RESULT

_BINARY_MATCHER = re.compile(r'"([\da-f]*)"b')

@_consume_leading_whitespace
def _binary_parser(s):
    match = _BINARY_MATCHER.match(s)

    if match:
        return _shared.ParseResult(
            success = True,
            value = binascii.unhexlify(match.group(1)),
            remaining = s[match.end():],
        )

    return _shared._FAILED_PARSE_RESULT

def _make_utf_parser(encoding):
    matcher = re.compile(r'"(.*?)"' + encoding)

    @_consume_leading_whitespace
    def utf_parser(s):
        match = matcher.match(s)

        if match:
            return _shared.ParseResult(
                success = True,
                value = match.group(1),
                remaining = s[match.end():],
            )

        return _shared._FAILED_PARSE_RESULT

    return utf_parser

def _make_consume_constant_parser(constant):
    @_consume_leading_whitespace
    def consume_character_parser(s):
        if s.startswith(constant):
            return _shared.ParseResult(
                success = True,
                value = None,
                remaining = s[len(constant):],
            )
        return _shared._FAILED_PARSE_RESULT

    return consume_character_parser

_consume_comma_parser = _make_consume_constant_parser(',')

def _prefix_with_comma(parser):
    def wrapped(s):
        result = _consume_comma_parser(s)
        if result.success:
            s = result.remaining
        else:
            return _shared._FAILED_PARSE_RESULT

        result = parser(s)
        if not result.success:
            raise Exception('Trailing comma before "{}"'.format(s))

        return result

    return wrapped

def _comma_separate_and_wrap(wrapped_parser, start_wrap, end_wrap, typecaster):
    parser_prefixed_with_comma = _prefix_with_comma(wrapped_parser)
    start_wrap_parser = _make_consume_constant_parser(start_wrap)
    end_wrap_parser = _make_consume_constant_parser(end_wrap)

    def parser(s):
        result = start_wrap_parser(s)
        if result.success:
            s = result.remaining
        else:
            return _shared._FAILED_PARSE_RESULT

        value = []
        first = True

        parse_result = wrapped_parser(s)

        while parse_result.success:
            value.append(parse_result.value)
            s = parse_result.remaining
            parse_result = parser_prefixed_with_comma(s)

        result = end_wrap_parser(s)
        if result.success:
            s = result.remaining
        else:
            return _shared._FAILED_PARSE_RESULT

        return _shared.ParseResult(
            success = True,
            value = typecaster(value),
            remaining = s,
        )

    return parser

# This uses _PARSERS which has not been defined yet, but is defined here so it can be used in
# the definition of _list_parser
def _object_parser(source):
    for parser in _PARSERS:
        result = parser(source)

        if result.success:
            return result

    return _shared._FAILED_PARSE_RESULT

_list_parser = _comma_separate_and_wrap(_object_parser, '[', ']', list)

_consume_colon_parser = _make_consume_constant_parser(':')

def _kvp_parser(s):
    key_parse_result = _object_parser(s)
    if key_parse_result.success:
        s = key_parse_result.remaining
    else:
        return _shared._FAILED_PARSE_RESULT

    result = _consume_colon_parser(s)
    if result.success:
        s = result.remaining
    else:
        return _shared._FAILED_PARSE_RESULT

    value_parse_result = _object_parser(s)
    if value_parse_result.success:
        s = value_parse_result.remaining
    else:
        return _shared._FAILED_PARSE_RESULT

    return _shared.ParseResult(
        success = True,
        value = (key_parse_result.value, value_parse_result.value),
        remaining = s,
    )

_dictionary_parser = _comma_separate_and_wrap(_kvp_parser, '{', '}', collections.OrderedDict)


_PARSERS = [
    _make_constant_parser('null', None),
    _make_constant_parser('true', True),
    _make_constant_parser('false', False),
    _make_integer_parser(8),
    _make_integer_parser(16),
    _make_integer_parser(32),
    _make_integer_parser(64),
    _binary32_parser,
    _binary64_parser,
    _binary_parser,
    _make_utf_parser('utf8'),
    _make_utf_parser('utf16'),
    _make_utf_parser('utf32'),
    _list_parser,
    _dictionary_parser,
]

def _parse(parser, source):
    result = parser(source)

    if result.success:
        if result.remaining.strip() == '':
            return result.value

        raise Exception('Unparsed trailing characters: "{}"'.format(result.remaining))

    raise Exception('Unable to parse: "{}"'.format(source))

def deserialize(s):
    return _parse(_object_parser, s)
