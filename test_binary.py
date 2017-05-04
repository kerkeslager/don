# -*- coding: utf-8 -*-
import collections
import unittest

from ton import binary, tags

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

    def test_serializes_binary(self):
        self.assertEqual(binary.serialize(b'\xde\xad\xbe\xef'), b'\x30\x00\x00\x00\x04\xde\xad\xbe\xef')

    def test_serializes_utf8(self):
        self.assertEqual(
            binary.serialize('Hello, world'),
            b'\x31\x00\x00\x00\x0cHello, world',
        )
        self.assertEqual(
            binary.serialize('世界'),
            b'\x31\x00\x00\x00\x06\xe4\xb8\x96\xe7\x95\x8c',
        )

    def test_serializes_list(self):
        self.assertEqual(binary.serialize([]),                                  b'\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize([1,2,3]),                             b'\x40\x12\x00\x00\x00\x0c\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03')
        self.assertEqual(binary.serialize(['Hello, world', 'Goodnight, moon']), b'\x40\x31\x00\x00\x00#\x00\x00\x00\x02\x00\x00\x00\x0cHello, world\x00\x00\x00\x0fGoodnight, moon')

    def test_serializes_dictionary(self):
        self.assertEqual(binary.serialize({}), b'\x41\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(binary.serialize(collections.OrderedDict([
            ('foo',42),
            ('bar','baz'),
        ])), b'A\x00\x00\x00\x1d\x00\x00\x00\x021\x00\x00\x00\x03foo\x12\x00\x00\x00*1\x00\x00\x00\x03bar1\x00\x00\x00\x03baz')

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

unittest.main()
