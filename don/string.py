import binascii
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
    o = tags._tag(o)
    
    return _STRING_SERIALIZERS[o.tag](o.value)

def _make_constant_parser(constant, value):
    def parser(s):
        if s.startswith(constant):
            result = _shared.ParseResult(
                success = True,
                value = value,
                remaining = s[len(constant):],
            )
            return result

        return _shared._FAILED_PARSE_RESULT

    return parser

def _make_integer_parser(width):
    matcher = re.compile(r'(-?\d+)i' + str(width))

    def parser(s):
        match = matcher.match(s)

        if match:
            return _shared.ParseResult(
                success = True,
                value = int(match.group(1)),
                remaining = s[match.end():],
            )

        return _shared._FAILED_PARSE_RESULT

    return parser

_PARSERS = [
    _make_constant_parser('null', None),
    _make_constant_parser('true', True),
    _make_constant_parser('false', False),
    _make_integer_parser(8),
    _make_integer_parser(16),
    _make_integer_parser(32),
    _make_integer_parser(64),
]

def _object_parser(source):
    for parser in _PARSERS:
        result = parser(source)

        if result.success:
            return result

    return _shared._FAILED_PARSE_RESULT

def _parse(parser, source):
    result = parser(source)

    if result.success:
        if result.remaining.strip() == '':
            return result.value

        raise Exception('Unparsed trailing characters: "{}"'.format(result.remaining))

    raise Exception('Unable to parse: "{}"'.format(source))

def deserialize(s):
    return _parse(_object_parser, s)
