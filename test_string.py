import collections
import unittest

from don import string, tags

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

    def test_deserializes_null_with_leading_whitespace(self):
        self.assertEqual(
            None,
            string.deserialize(' \t\nnull'),
        )

    def test_deserializes_true(self):
        self.assertEqual(
            True,
            string.deserialize('true'),
        )

    def test_deserializes_true_with_leading_whitespace(self):
        self.assertEqual(
            True,
            string.deserialize(' \t\ntrue'),
        )

    def test_deserializes_false(self):
        self.assertEqual(
            False,
            string.deserialize('false'),
        )

    def test_deserializes_false_with_leading_whitespace(self):
        self.assertEqual(
            False,
            string.deserialize(' \t\nfalse'),
        )

    def test_deserializes_int8(self):
        self.assertEqual(10, string.deserialize('10i8'))
        self.assertEqual(-1, string.deserialize('-1i8'))

    def test_deserializes_int8_with_leading_whitespace(self):
        self.assertEqual(10, string.deserialize(' \t\n10i8'))
        self.assertEqual(-1, string.deserialize(' \t\n-1i8'))

    def test_deserializes_int16(self):
        self.assertEqual(10, string.deserialize('10i16'))
        self.assertEqual(-1, string.deserialize('-1i16'))

    def test_deserializes_int16_with_leading_whitespace(self):
        self.assertEqual(10, string.deserialize(' \t\n10i16'))
        self.assertEqual(-1, string.deserialize(' \t\n-1i16'))

    def test_deserializes_int32(self):
        self.assertEqual(10, string.deserialize('10i32'))
        self.assertEqual(-1, string.deserialize('-1i32'))

    def test_deserializes_int32_with_leading_whitespace(self):
        self.assertEqual(10, string.deserialize(' \t\n10i32'))
        self.assertEqual(-1, string.deserialize(' \t\n-1i32'))

    def test_deserializes_int64(self):
        self.assertEqual(10, string.deserialize('10i64'))
        self.assertEqual(-1, string.deserialize('-1i64'))

    def test_deserializes_int64_with_leading_whitespace(self):
        self.assertEqual(10, string.deserialize(' \t\n10i64'))
        self.assertEqual(-1, string.deserialize(' \t\n-1i64'))

    def test_deserializes_binary(self):
        self.assertEqual(
            b'\xde\xad\xbe\xef',
            string.deserialize('"deadbeef"b'),
        )

    def test_deserializes_binary_with_leading_whitespace(self):
        self.assertEqual(
            b'\xde\xad\xbe\xef',
            string.deserialize(' \t\n"deadbeef"b'),
        )

    def test_deserializes_utf8(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize('"Hello, world"utf8'),
        )

    def test_deserializes_utf16(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize('"Hello, world"utf16'),
        )

    def test_deserializes_utf32(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize('"Hello, world"utf32'),
        )

    def test_deserializes_utf8_with_leading_whitespace(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize(' \t\n"Hello, world"utf8'),
        )

    def test_deserializes_utf16_with_leading_whitespace(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize(' \t\n"Hello, world"utf16'),
        )

    def test_deserializes_utf32_with_leading_whitespace(self):
        self.assertEqual(
            "Hello, world",
            string.deserialize(' \t\n"Hello, world"utf32'),
        )

    def test_deserializes_list(self):
        self.assertEqual(
            [1,2,3,4,5],
            string.deserialize("[1i8,2i8,3i8,4i8,5i8]"),
        )

    def test_deserializes_list_with_leading_whitespace(self):
        self.assertEqual(
            [1,2,3,4,5],
            string.deserialize(" \t\n[ \t\n1i8 \t\n, \t\n2i8 \t\n, \t\n3i8 \t\n, \t\n4i8 \t\n, \t\n5i8 \t\n]"),
        )

    def test_deserializes_dictionary(self):
        self.assertEqual(
            collections.OrderedDict([
                ('foo', 1),
                ('bar', 'baz'),
            ]),
            string.deserialize('{"foo"utf8:1i32,"bar"utf8:"baz"utf8}'),
        )

    def test_deserializes_dictionary_with_leading_whitespace(self):
        self.assertEqual(
            collections.OrderedDict([
                ('foo', 1),
                ('bar', 'baz'),
            ]),
            string.deserialize(' \t\n{ \t\n"foo"utf8 \t\n: \t\n1i32 \t\n, \t\n"bar"utf8 \t\n: \t\n"baz"utf8 \t\n}'),
        )

unittest.main()
