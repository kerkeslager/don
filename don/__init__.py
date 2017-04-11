import collections
import struct

from don import binary
from don import string
from don.constants import *
from don._shared import TaggedObject

def binary_to_string(b):
    return string.serialize(binary.deserialize(b))

def string_to_binary(s):
    return binary.serialize(string.deserialize(s))
