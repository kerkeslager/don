TON: Twofold Object Notation
============================

TON is a twofold object notation with equivalent binary and human-readable
forms. The binary form is optimized for speed and size, while the human-
readable form is designed to be easy-to-understand. Every TON object in binary
representation has one unambiguously equivalent TON string representation
(ignoring whitespace), and every TON object in string representation has one
unambiguously equivalent TON binary representation. This means that you can
use the binary representation and get all the benefits of binary, but if you
need to inspect the contents of the binary it's simple to convert it to the
string notation and get all the benefits of a human-readable representation.

Without further ado, here's what the human-readable representation looks like:::

    {
      'foo'utf8: 1i8,
      'bar'utf8: 'baz'utf16,
      'qux'utf8: [1i16, -1i16],
      'quux'utf8: [2i32, -2i32],
      'quuz'utf8: [3i64, -3i64]
    }
