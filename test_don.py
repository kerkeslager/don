import collections
import unittest

from don import binary, string, tags

class TestBinarySerialize(unittest.TestCase):
    def test_serializes_null(self):
        self.assertEqual(binary.serialize(None), b'\x00')

    def test_serializes_true(self):
        self.assertEqual(binary.serialize(True), b'\x01')

    def test_serializes_false(self):
        self.assertEqual(binary.serialize(False), b'\x02')

    def test_serializes_integers_in_32_bit_twos_complement_with_network_byte_order(self):
        self.assertEqual(binary.serialize(-2147483648), b'\x12\x80\x00\x00\x00')
        self.assertEqual(binary.serialize(-1),          b'\x12\xff\xff\xff\xff')
        self.assertEqual(binary.serialize(0),           b'\x12\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(1),           b'\x12\x00\x00\x00\x01')
        self.assertEqual(binary.serialize(2147483647),  b'\x12\x7f\xff\xff\xff')

    def test_serializes_floats_into_binary64_with_network_byte_order(self):
        self.assertEqual(binary.serialize(1.0),          b'\x21\x3f\xf0\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(2.0),          b'\x21\x40\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(-2.0),         b'\x21\xc0\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(0.5),          b'\x21\x3f\xe0\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(2.0 ** -1074), b'\x21\x00\x00\x00\x00\x00\x00\x00\x01')
        self.assertEqual(binary.serialize(2.0 ** -1022), b'\x21\x00\x10\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(0.0),          b'\x21\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_serializes_binary(self):
        self.assertEqual(binary.serialize(b'\xde\xad\xbe\xef'), b'\x30\x00\x00\x00\x04\xde\xad\xbe\xef')

    def test_serializes_utf8(self):
        self.assertEqual(binary.serialize('Hello, world'), b'\x31\x00\x00\x00\x0cHello, world')
        self.assertEqual(binary.serialize('世界'),         b'\x31\x00\x00\x00\x06\xe4\xb8\x96\xe7\x95\x8c')

    def test_serializes_list(self):
        self.assertEqual(binary.serialize([]),                                  b'\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize([1,2,3]),                             b'\x40\x12\x00\x00\x00\x0c\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03')
        self.assertEqual(binary.serialize(['Hello, world', 'Goodnight, moon']), b'\x40\x31\x00\x00\x00#\x00\x00\x00\x02\x00\x00\x00\x0cHello, world\x00\x00\x00\x0fGoodnight, moon')
        self.assertEqual(binary.serialize([1.618, 2.718, 3.142]),               b'\x40\x21\x00\x00\x00\x18\x00\x00\x00\x03?\xf9\xe3S\xf7\xce\xd9\x17@\x05\xbev\xc8\xb49X@\t"\xd0\xe5`A\x89')

    def test_serializes_dictionary(self):
        self.assertEqual(binary.serialize({}), b'\x41\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(collections.OrderedDict([
            ('foo',42),
            ('bar',3.14),
            ('baz','qux'),
        ])), b'A\x00\x00\x00+\x00\x00\x00\x03\x00\x00\x00\x03foo\x12\x00\x00\x00*\x00\x00\x00\x03bar!@\t\x1e\xb8Q\xeb\x85\x1f\x00\x00\x00\x03baz1\x00\x00\x00\x03qux')

class TestBinaryDeserialize(unittest.TestCase):
    def test_deserializes_null(self):
        self.assertEqual(binary.deserialize(b'\x00'), None)

    def test_deserializes_true(self):
        self.assertEqual(binary.deserialize(b'\x01'), True)

    def test_deserializes_false(self):
        self.assertEqual(binary.deserialize(b'\x02'), False)

    def test_deserializes_8_bit_twos_complement_with_network_byte_order(self):
        self.assertEqual(binary.deserialize(b'\x10\x80'), -128)
        self.assertEqual(binary.deserialize(b'\x10\xff'), -1)
        self.assertEqual(binary.deserialize(b'\x10\x00'), 0)
        self.assertEqual(binary.deserialize(b'\x10\x01'), 1)
        self.assertEqual(binary.deserialize(b'\x10\x7f'), 127)

    def test_deserializes_16_bit_twos_complement_with_network_byte_order(self):
        self.assertEqual(binary.deserialize(b'\x11\x80\x00'), -32768)
        self.assertEqual(binary.deserialize(b'\x11\xff\xff'), -1)
        self.assertEqual(binary.deserialize(b'\x11\x00\x00'), 0)
        self.assertEqual(binary.deserialize(b'\x11\x00\x01'), 1)
        self.assertEqual(binary.deserialize(b'\x11\x7f\xff'), 32767)

    def test_deserializes_32_bit_twos_complement_with_network_byte_order(self):
        self.assertEqual(binary.deserialize(b'\x12\x80\x00\x00\x00'), -2147483648)
        self.assertEqual(binary.deserialize(b'\x12\xff\xff\xff\xff'), -1)
        self.assertEqual(binary.deserialize(b'\x12\x00\x00\x00\x00'), 0)
        self.assertEqual(binary.deserialize(b'\x12\x00\x00\x00\x01'), 1)
        self.assertEqual(binary.deserialize(b'\x12\x7f\xff\xff\xff'), 2147483647)

    def test_deserializes_64_bit_twos_complement_with_network_byte_order(self):
        self.assertEqual(binary.deserialize(b'\x13\x80\x00\x00\x00\x00\x00\x00\x00'), -9223372036854775808)
        self.assertEqual(binary.deserialize(b'\x13\xff\xff\xff\xff\xff\xff\xff\xff'), -1)
        self.assertEqual(binary.deserialize(b'\x13\x00\x00\x00\x00\x00\x00\x00\x00'), 0)
        self.assertEqual(binary.deserialize(b'\x13\x00\x00\x00\x00\x00\x00\x00\x01'), 1)
        self.assertEqual(binary.deserialize(b'\x13\x7f\xff\xff\xff\xff\xff\xff\xff'), 9223372036854775807)

    def test_deserializes_binary64_as_float(self):
        self.assertEqual(binary.deserialize(b'\x21\x3f\xf0\x00\x00\x00\x00\x00\x00'), 1.0)
        self.assertEqual(binary.deserialize(b'\x21\x40\x00\x00\x00\x00\x00\x00\x00'), 2.0)
        self.assertEqual(binary.deserialize(b'\x21\xc0\x00\x00\x00\x00\x00\x00\x00'), -2.0)
        self.assertEqual(binary.deserialize(b'\x21\x3f\xe0\x00\x00\x00\x00\x00\x00'), 0.5)
        self.assertEqual(binary.deserialize(b'\x21\x00\x00\x00\x00\x00\x00\x00\x01'), 2.0 ** -1074)
        self.assertEqual(binary.deserialize(b'\x21\x00\x10\x00\x00\x00\x00\x00\x00'), 2.0 ** -1022)
        self.assertEqual(binary.deserialize(b'\x21\x00\x00\x00\x00\x00\x00\x00\x00'), 0.0)

    def test_deserializes_binary(self):
        self.assertEqual(binary.deserialize(b'\x30\x00\x00\x00\x04\xde\xad\xbe\xef'), b'\xde\xad\xbe\xef')

    def test_deserializes_utf8(self):
        self.assertEqual(binary.deserialize(b'\x31\x00\x00\x00\x0cHello, world'),             'Hello, world')
        self.assertEqual(binary.deserialize(b'\x31\x00\x00\x00\x06\xe4\xb8\x96\xe7\x95\x8c'), '世界')

    def test_deserializes_lists(self):
        self.assertEqual(list(binary.deserialize(b'\x40\x12\x00\x00\x00\x00\x00\x00\x00\x00')), [])
        self.assertEqual(list(binary.deserialize(b'\x40\x12\x00\x00\x00\x0c\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03')), [1,2,3])

    def test_deserializes_dictionaries(self):
        self.assertEqual(binary.deserialize(b'\x41\x00\x00\x00\x00\x00\x00\x00\x00'), collections.OrderedDict([]))
        self.assertEqual(binary.deserialize(b'\x41\x00\x00\x00\x1b\x00\x00\x00\x02\x00\x00\x00\x03foo\x12\x00\x00\x00\x2a\x00\x00\x00\x03bar\x31\x00\x00\x00\x03baz'), collections.OrderedDict([('foo',42), ('bar','baz')]))


class TestStringSerialize(unittest.TestCase):
    def test_serializes_null(self):
        self.assertEqual(string.serialize(None), 'null')

    def test_serializes_true(self):
        self.assertEqual(string.serialize(True), 'true')

    def test_serializes_false(self):
        self.assertEqual(string.serialize(False), 'false')

    def test_serializes_int8(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT8, 1)), '1i8')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT8, -1)), '-1i8')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT8, 42)), '42i8')

    def test_serializes_int16(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT16, 1)), '1i16')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT16, -1)), '-1i16')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT16, 42)), '42i16')

    def test_serializes_int32(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT32, 1)), '1i32')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT32, -1)), '-1i32')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT32, 42)), '42i32')

    def test_serializes_int64(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT64, 1)), '1i64')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT64, -1)), '-1i64')
        self.assertEqual(string.serialize(tags.TaggedObject(tags.INT64, 42)), '42i64')

    def test_serializes_float(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.FLOAT, 1.0)), '1.0f')

    def test_serializes_double(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.DOUBLE, 1.0)), '1.0d')

    def test_serializes_binary(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.BINARY, b'\xde\xad\xbe\xef')), '"deadbeef"b')

    def test_serializes_utf8(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.UTF8, 'Hello, world')), '"Hello, world"utf8')

    def test_serializes_utf16(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.UTF16, 'Hello, world')), '"Hello, world"utf16')

    def test_serializes_utf32(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.UTF32, 'Hello, world')), '"Hello, world"utf32')

    def test_serializes_list(self):
        self.assertEqual(string.serialize(tags.TaggedObject(tags.LIST, [1,2,3])), '[1i32, 2i32, 3i32]')

    def test_serializes_dictionary(self):
        self.assertEqual(
            string.serialize(tags.TaggedObject(tags.DICTIONARY, collections.OrderedDict([
                ('foo', 1),
                ('bar', 'baz'),
            ]))),
            '{ "foo"utf8: 1i32, "bar"utf8: "baz"utf8 }'
        )

class TestStringDeserialize(unittest.TestCase):
    def test_deserializes_null(self):
        self.assertEqual(
            None,
            string.deserialize('null'),
        )

    def test_deserializes_null(self):
        self.assertEqual(
            True,
            string.deserialize('true'),
        )

    def test_deserializes_null(self):
        self.assertEqual(
            False,
            string.deserialize('false'),
        )

    def test_deserializes_int8(self):
        self.assertEqual(10, string.deserialize('10i8'))
        self.assertEqual(-1, string.deserialize('-1i8'))

    def test_deserializes_int16(self):
        self.assertEqual(10, string.deserialize('10i16'))
        self.assertEqual(-1, string.deserialize('-1i16'))

    def test_deserializes_int32(self):
        self.assertEqual(10, string.deserialize('10i32'))
        self.assertEqual(-1, string.deserialize('-1i32'))

    def test_deserializes_int64(self):
        self.assertEqual(10, string.deserialize('10i64'))
        self.assertEqual(-1, string.deserialize('-1i64'))

    def test_deserializes_float(self):
        self.assertEqual(1.0, string.deserialize('1.0f'))

    def test_deserializes_double(self):
        self.assertEqual(1.0, string.deserialize('1.0d'))

    def test_serializes_binary(self):
        self.assertEqual(
            b'\xde\xad\xbe\xef',
            string.deserialize(b'\x30\x00\x00\x00\x04\xde\xad\xbe\xef'),
        )

    def test_serializes_binary(self):
        self.assertEqual(
            b'\xde\xad\xbe\xef',
            string.deserialize('"deadbeef"b'),
        )

unittest.main()
