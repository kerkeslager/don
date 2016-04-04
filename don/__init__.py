import binascii
import collections
import struct

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

def _binary_serialize_tag_only_type(o):
    return b''

def _pack_format_string_to_binary_serializer(pfs):
    def serializer(i):
        return struct.pack(pfs, i)
    return serializer

def _encoder_to_binary_serializer(e):
    def serializer(s):
        encoded = e(s)
        return struct.pack('!I', len(encoded)) + encoded
    return serializer

def _binary_serialize_list(items):
    # TODO Enforce that items are all the same type
    items = [_tag(i) for i in items]

    if len(items) == 0:
        item_tag = VOID
    else:
        item_tag = items[0].tag

    item_serializer = _BINARY_SERIALIZERS[item_tag]
    items = [item_serializer(i.value) for i in items]
    item_length = len(items)
    items = b''.join(items)
    byte_length = len(items)
    return struct.pack('!BII', item_tag, byte_length, item_length) + items

def _binary_serialize_dict(d):
    item_length = 0
    serialized = b''

    key_serializer = _BINARY_SERIALIZERS[UTF8]

    for key, value in d.items():
        assert isinstance(key, str)
        item_length += 1
        serialized += key_serializer(key) + _binary_serialize(value)

    byte_length = len(serialized)
    return struct.pack('!II', byte_length, item_length) + serialized

_BINARY_SERIALIZERS = {
    VOID: _binary_serialize_tag_only_type,
    TRUE: _binary_serialize_tag_only_type,
    FALSE: _binary_serialize_tag_only_type,
    INT8: _pack_format_string_to_binary_serializer('!b'),
    INT16: _pack_format_string_to_binary_serializer('!h'),
    INT32: _pack_format_string_to_binary_serializer('!i'),
    FLOAT: _pack_format_string_to_binary_serializer('!f'),
    DOUBLE: _pack_format_string_to_binary_serializer('!d'),
    BINARY: _encoder_to_binary_serializer(lambda b: b),
    UTF8: _encoder_to_binary_serializer(lambda s: s.encode('utf-8')),
    UTF16: _encoder_to_binary_serializer(lambda s: s.encode('utf-16')),
    UTF32: _encoder_to_binary_serializer(lambda s: s.encode('utf-32')),
    LIST: _binary_serialize_list,
    DICTIONARY: _binary_serialize_dict,
}

def _binary_serialize(o):
    o = _tag(o)
    return struct.pack('!B', o.tag) + _BINARY_SERIALIZERS[o.tag](o.value)

ParseResult = collections.namedtuple(
    'ParseResult',
    [
        'success',
        'value',
        'remaining',
    ],
)

_FAILED_PARSE_RESULT = ParseResult(success = False, value = None, remaining = None)

_BYTE_SIZES_TO_UNPACK_FORMATS = {
    1: '!b',
    2: '!h',
    4: '!i',
    8: '!q',
}

def make_integer_parser(size_in_bytes):
    unpack_format = _BYTE_SIZES_TO_UNPACK_FORMATS[size_in_bytes]

    def integer_parser(source):
        value = struct.unpack(unpack_format, source[:size_in_bytes])[0]
        remaining = source[size_in_bytes:]

        return ParseResult(success = True, value = value, remaining = remaining)

    return integer_parser

def binary64_parser(source):
    return ParseResult(
        success = True,
        value = struct.unpack('!d', source[:8])[0],
        remaining = source[8:],
    )

def make_string_parser(decoder):
    def string_parser(source):
        length = struct.unpack('!I', source[:4])[0]
        source = source[4:]
        return ParseResult(
            success = True,
            value = decoder(source[:length]),
            remaining = source[length:],
        )

    return string_parser

def _list_parser(source):
    tag = source[0]
    parser = _TAGS_TO_PARSERS[tag]

    source = source[1:]
    byte_length, items_length = struct.unpack('!II', source[:8])
    source = source[8:]

    remaining = source[byte_length:]
    source = source[:byte_length]

    def item_iterator(source):
        count = 0

        while len(source) > 0:
            parse_result = parser(source)

            if parse_result.success:
                count += 1
                yield parse_result.value
                source = parse_result.remaining

        assert count == items_length
    
    return ParseResult(
        success = True,
        value = item_iterator(source),
        remaining = remaining,
    )

def dictionary_parser(source):
    key_parser = _TAGS_TO_PARSERS[UTF8]

    byte_length, item_length = struct.unpack('!II', source[:8])
    source = source[8:]

    remaining = source[byte_length:]
    source = source[:byte_length]

    def kvp_iterator(source):
        count = 0

        while len(source) > 0:
            count += 1
            key_parse_result = key_parser(source)
            key, source = key_parse_result.value, key_parse_result.remaining
            value_parse_result = _object_parser(source)
            value, source = value_parse_result.value, value_parse_result.remaining

            yield key, value

        assert count == item_length

    return ParseResult(
        success = True,
        value = collections.OrderedDict(kvp_iterator(source)),
        remaining = remaining,
    )


_TAGS_TO_PARSERS = {
    VOID: lambda r: ParseResult(True, None, r),
    TRUE: lambda r: ParseResult(True, True, r),
    FALSE: lambda r: ParseResult(True, False, r),
    INT8: make_integer_parser(1),
    INT16: make_integer_parser(2),
    INT32: make_integer_parser(4),
    INT64: make_integer_parser(8),
    DOUBLE: binary64_parser,
    BINARY: make_string_parser(lambda b : b),
    UTF8: make_string_parser(lambda b : b.decode('utf-8')),
    UTF16: make_string_parser(lambda b : b.decode('utf-16')),
    UTF32: make_string_parser(lambda b : b.decode('utf-32')),
    LIST: _list_parser,
    DICTIONARY: dictionary_parser,
}

def _object_parser(source):
    return _TAGS_TO_PARSERS[source[0]](source[1:])

def _parse(parser, source, consume_all = True):
    result = parser(source)

    if result.success and result.remaining == b'':
        return result.value

    raise Exception('Unparsed trailing bytes: {}'.format(result.remaining))

def _binary_deserialize(b):
    return _parse(_object_parser, b)

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
    return '[{}]'.format(', '.join(map(_string_serialize, l)))

def _string_serialize_dictionary(d):
    def serialize_kvp(kvp):
        return _string_serialize(kvp[0]) + ': ' + _string_serialize(kvp[1])
    return '{ ' + ', '.join(map(serialize_kvp, d.items())) + ' }'

_STRING_SERIALIZERS = {
    VOID: lambda o: 'null',
    TRUE: lambda o: 'true',
    FALSE: lambda o: 'false',
    INT8: _integer_size_to_string_serializer(8),
    INT16: _integer_size_to_string_serializer(16),
    INT32: _integer_size_to_string_serializer(32),
    INT64: _integer_size_to_string_serializer(64),
    FLOAT: _serialize_float,
    DOUBLE: _serialize_double,
    BINARY: _serialize_binary,
    UTF8: _utf_encoding_to_serializer('utf8'),
    UTF16: _utf_encoding_to_serializer('utf16'),
    UTF32: _utf_encoding_to_serializer('utf32'),
    LIST: _string_serialize_list,
    DICTIONARY: _string_serialize_dictionary,
}

def _string_serialize(o):
    o = _tag(o)
    
    return _STRING_SERIALIZERS[o.tag](o.value)

def _string_deserialize(o):
    pass

Serializer = collections.namedtuple('Serializer', ['serialize', 'deserialize'])

binary = Serializer(
    serialize = _binary_serialize,
    deserialize = _binary_deserialize,
)

string = Serializer(
    serialize = _string_serialize,
    deserialize = _string_deserialize,
)

def binary_to_string(b):
    return string.serialize(binary.deserialize(b))

def string_to_binary(s):
    return binary.serialize(string.deserialize(s))
