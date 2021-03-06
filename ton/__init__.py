import collections
import struct

from ton import binary, string

def binary_to_string(b):
    return string.serialize(binary.deserialize(b))

def string_to_binary(s):
    return binary.serialize(string.deserialize(s))
