import collections
import unittest

from ton import tags

class AutoTagTests(unittest.TestCase):
    def test_autotags_void(self):
        self.assertEqual(
            tags.autotag(None),
            tags.TaggedObject(tag = tags.VOID, value = None),
        )

    def test_autotags_true(self):
        self.assertEqual(
            tags.autotag(True),
            tags.TaggedObject(tag = tags.TRUE, value = True),
        )

    def test_autotags_false(self):
        self.assertEqual(
            tags.autotag(False),
            tags.TaggedObject(tag = tags.FALSE, value = False),
        )

    def test_autotags_int_defaults_to_INT32(self):
        self.assertEqual(
            tags.autotag(127),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = 127),
        )
        self.assertEqual(
            tags.autotag(-128),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = -128),
        )
        self.assertEqual(
            tags.autotag(128),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = 128),
        )
        self.assertEqual(
            tags.autotag(-129),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = -129),
        )
        self.assertEqual(
            tags.autotag(-32768),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = -32768),
        )
        self.assertEqual(
            tags.autotag(32767),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = 32767),
        )
        self.assertEqual(
            tags.autotag(-32769),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = -32769),
        )
        self.assertEqual(
            tags.autotag(32768),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = 32768),
        )
        self.assertEqual(
            tags.autotag(-2147483648),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = -2147483648),
        )
        self.assertEqual(
            tags.autotag(2147483647),
            tags.TaggedObject(tag = tags.DEFAULT_INTEGER_ENCODING, value = 2147483647),
        )
        self.assertEqual(
            tags.autotag(-2147483649),
            tags.TaggedObject(tag = tags.INT64, value = -2147483649),
        )
        self.assertEqual(
            tags.autotag(2147483648),
            tags.TaggedObject(tag = tags.INT64, value = 2147483648),
        )
        self.assertEqual(
            tags.autotag(-9223372036854775808),
            tags.TaggedObject(tag = tags.INT64, value = -9223372036854775808),
        )
        self.assertEqual(
            tags.autotag(9223372036854775807),
            tags.TaggedObject(tag = tags.INT64, value = 9223372036854775807),
        )
        
        with self.assertRaises(tags.TooWideError):
            tags.autotag(9223372036854775808)

        with self.assertRaises(tags.TooWideError):
            tags.autotag(-9223372036854775809)

    def test_autotags_int_to_smallest_possible_type_when_preferred_type_is_smallest(self):
        self.assertEqual(
            tags.autotag(127, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT8, value = 127),
        )
        self.assertEqual(
            tags.autotag(-128, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT8, value = -128),
        )
        self.assertEqual(
            tags.autotag(128, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT16, value = 128),
        )
        self.assertEqual(
            tags.autotag(-129, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT16, value = -129),
        )
        self.assertEqual(
            tags.autotag(-32768, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT16, value = -32768),
        )
        self.assertEqual(
            tags.autotag(32767, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT16, value = 32767),
        )
        self.assertEqual(
            tags.autotag(-32769, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT32, value = -32769),
        )
        self.assertEqual(
            tags.autotag(32768, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT32, value = 32768),
        )
        self.assertEqual(
            tags.autotag(-2147483648, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT32, value = -2147483648),
        )
        self.assertEqual(
            tags.autotag(2147483647, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT32, value = 2147483647),
        )
        self.assertEqual(
            tags.autotag(-2147483649, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT64, value = -2147483649),
        )
        self.assertEqual(
            tags.autotag(2147483648, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT64, value = 2147483648),
        )
        self.assertEqual(
            tags.autotag(-9223372036854775808, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT64, value = -9223372036854775808),
        )
        self.assertEqual(
            tags.autotag(9223372036854775807, preferred_integer_tag=tags.SMALLEST),
            tags.TaggedObject(tag = tags.INT64, value = 9223372036854775807),
        )
        
        with self.assertRaises(tags.TooWideError):
            tags.autotag(9223372036854775808, preferred_integer_tag=tags.SMALLEST)

        with self.assertRaises(tags.TooWideError):
            tags.autotag(-9223372036854775809, preferred_integer_tag=tags.SMALLEST)

    def test_tags_integer_to_preferred_integer_tag(self):
        self.assertEqual(
            tags.autotag(42, preferred_integer_tag = tags.INT8),
            tags.TaggedObject(tag = tags.INT8, value = 42),
        )

        self.assertEqual(
            tags.autotag(42, preferred_integer_tag = tags.INT16),
            tags.TaggedObject(tag = tags.INT16, value = 42),
        )

        self.assertEqual(
            tags.autotag(42, preferred_integer_tag = tags.INT32),
            tags.TaggedObject(tag = tags.INT32, value = 42),
        )

        self.assertEqual(
            tags.autotag(42, preferred_integer_tag = tags.INT64),
            tags.TaggedObject(tag = tags.INT64, value = 42),
        )

    def test_tags_string_to_utf8_by_default(self):
        self.assertEqual(
            tags.autotag('Hello, world'),
            tags.TaggedObject(tag = tags.DEFAULT_STRING_ENCODING, value = 'Hello, world'),
        )

    def test_tags_string_to_preferred_string_encoding(self):
        self.assertEqual(
            tags.autotag('Hello, world', preferred_string_tag=tags.UTF8),
            tags.TaggedObject(tag = tags.UTF8, value = 'Hello, world'),
        )

        self.assertEqual(
            tags.autotag('Hello, world', preferred_string_tag=tags.UTF16),
            tags.TaggedObject(tag = tags.UTF16, value = 'Hello, world'),
        )

        self.assertEqual(
            tags.autotag('Hello, world', preferred_string_tag=tags.UTF32),
            tags.TaggedObject(tag = tags.UTF32, value = 'Hello, world'),
        )

    def test_tags_bytes(self):
        self.assertEqual(
            tags.autotag(b'\xde\xad\xbe\xef'),
            tags.TaggedObject(tag = tags.BINARY, value = b'\xde\xad\xbe\xef'),
        )

    def test_tags_list(self):
        self.assertEqual(
            tags.autotag([1,2,3]),
            tags.TaggedObject(
                tag = tags.LIST,
                value = [
                    tags.TaggedObject(tag = tags.INT32, value = 1),
                    tags.TaggedObject(tag = tags.INT32, value = 2),
                    tags.TaggedObject(tag = tags.INT32, value = 3),
                ],
            ),
        )

    def test_tags_dictionary(self):
        self.assertEqual(
            tags.autotag(collections.OrderedDict([
                ('foo', 1),
                ('bar', True),
            ])),
            tags.TaggedObject(
                tag = tags.DICTIONARY,
                value = collections.OrderedDict([
                    (
                        tags.TaggedObject(tag = tags.UTF8, value = 'foo'),
                        tags.TaggedObject(tag = tags.INT32, value = 1),
                    ),
                    (
                        tags.TaggedObject(tag = tags.UTF8, value = 'bar'),
                        tags.TaggedObject(tag = tags.TRUE, value = True),
                    ),
                ]),
            ),
        )

unittest.main()
