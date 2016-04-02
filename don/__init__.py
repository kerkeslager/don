import don.binary as binary
import don.string as string

def binary_to_string(b):
    return string.serialize(binary.deserialize(b))

def string_to_binary(s):
    return binary.serialize(string.deserialize(s))
