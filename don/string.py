import binascii

from don import constants, _shared

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
    constants.VOID: lambda o: 'null',
    constants.TRUE: lambda o: 'true',
    constants.FALSE: lambda o: 'false',
    constants.INT8: _integer_size_to_string_serializer(8),
    constants.INT16: _integer_size_to_string_serializer(16),
    constants.INT32: _integer_size_to_string_serializer(32),
    constants.INT64: _integer_size_to_string_serializer(64),
    constants.FLOAT: _serialize_float,
    constants.DOUBLE: _serialize_double,
    constants.BINARY: _serialize_binary,
    constants.UTF8: _utf_encoding_to_serializer('utf8'),
    constants.UTF16: _utf_encoding_to_serializer('utf16'),
    constants.UTF32: _utf_encoding_to_serializer('utf32'),
    constants.LIST: _string_serialize_list,
    constants.DICTIONARY: _string_serialize_dictionary,
}

def serialize(o):
    o = _shared._tag(o)
    
    return _STRING_SERIALIZERS[o.tag](o.value)

def deserialize(s):
    pass
