import collections
import struct

from don import tags, _shared

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
    items = [tags._tag(i) for i in items]

    if len(items) == 0:
        item_tag = tags.VOID
    else:
        item_tag = items[0].tag

    item_serializer = _BINARY_SERIALIZERS[item_tag]
    items = [item_serializer(i.value) for i in items]
    item_length = len(items)
    items = b''.join(items)
    byte_length = len(items)
    return struct.pack('!BII', item_tag, byte_length, item_length) + items

def _serialize_key(o):
    o = tags.autotag(o)
    assert o.tag in tags.STRING_TAGS
    return struct.pack('!B', o.tag) + _BINARY_SERIALIZERS[o.tag](o.value)

def _binary_serialize_dict(d):
    item_length = 0
    serialized = b''

    key_serializer = _BINARY_SERIALIZERS[tags.UTF8]

    for key, value in d.items():
        item_length += 1
        serialized += _serialize_key(key) + serialize(value)

    byte_length = len(serialized)
    return struct.pack('!II', byte_length, item_length) + serialized

_BINARY_SERIALIZERS = {
    tags.VOID: _binary_serialize_tag_only_type,
    tags.TRUE: _binary_serialize_tag_only_type,
    tags.FALSE: _binary_serialize_tag_only_type,
    tags.INT8: _pack_format_string_to_binary_serializer('!b'),
    tags.INT16: _pack_format_string_to_binary_serializer('!h'),
    tags.INT32: _pack_format_string_to_binary_serializer('!i'),
    tags.BINARY: _encoder_to_binary_serializer(lambda b: b),
    tags.UTF8: _encoder_to_binary_serializer(lambda s: s.encode('utf-8')),
    tags.UTF16: _encoder_to_binary_serializer(lambda s: s.encode('utf-16')),
    tags.UTF32: _encoder_to_binary_serializer(lambda s: s.encode('utf-32')),
    tags.LIST: _binary_serialize_list,
    tags.DICTIONARY: _binary_serialize_dict,
}

def serialize(o):
    o = tags.autotag(o)
    return struct.pack('!B', o.tag) + _BINARY_SERIALIZERS[o.tag](o.value)

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

        return _shared.ParseResult(success = True, value = value, remaining = remaining)

    return integer_parser

def binary64_parser(source):
    return _shared.ParseResult(
        success = True,
        value = struct.unpack('!d', source[:8])[0],
        remaining = source[8:],
    )

def make_string_parser(decoder):
    def string_parser(source):
        length = struct.unpack('!I', source[:4])[0]
        source = source[4:]
        return _shared.ParseResult(
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
    
    return _shared.ParseResult(
        success = True,
        value = item_iterator(source),
        remaining = remaining,
    )

def dictionary_parser(source):
    key_parser = _TAGS_TO_PARSERS[tags.UTF8]

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

    return _shared.ParseResult(
        success = True,
        value = collections.OrderedDict(kvp_iterator(source)),
        remaining = remaining,
    )


_TAGS_TO_PARSERS = {
    tags.VOID: lambda r: _shared.ParseResult(True, None, r),
    tags.TRUE: lambda r: _shared.ParseResult(True, True, r),
    tags.FALSE: lambda r: _shared.ParseResult(True, False, r),
    tags.INT8: make_integer_parser(1),
    tags.INT16: make_integer_parser(2),
    tags.INT32: make_integer_parser(4),
    tags.INT64: make_integer_parser(8),
    tags.BINARY: make_string_parser(lambda b : b),
    tags.UTF8: make_string_parser(lambda b : b.decode('utf-8')),
    tags.UTF16: make_string_parser(lambda b : b.decode('utf-16')),
    tags.UTF32: make_string_parser(lambda b : b.decode('utf-32')),
    tags.LIST: _list_parser,
    tags.DICTIONARY: dictionary_parser,
}

def _object_parser(source):
    return _TAGS_TO_PARSERS[source[0]](source[1:])

def _parse(parser, source):
    result = parser(source)

    if result.success and result.remaining == b'':
        return result.value

    raise Exception('Unparsed trailing bytes: {}'.format(result.remaining))

def deserialize(b):
    return _parse(_object_parser, b)
