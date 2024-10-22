import struct
from sys import exit
# The message after the first 4 bytes (remaining message)
remaining_message = b'\xCB\xCE\xB84\xCD\xB8h\x83@'


# warning:
# to decode floats, you need
# to use Little-endian...
# Example of a decoded value: 166.63718228327218
# input data was

# b'\xCB\xD4\x87\x19\xCCc\xD4d@'

# that is:
# 0xCB
# 0xD4 0x87 0x19 0xCC
# 0x67 0xD4 0x64 0x40
# warning! The last byte ("@") is indeed part of the number,
# i thought it was a marker but no its wrong

print(len(remaining_message))

# First byte is the marker (0xCB), so we skip it
float_bytes = remaining_message[1:9]

# Decode the FLOAT_64 (big-endian by default)
decoded_value_big_endian = struct.unpack('>d', float_bytes)[0]

# Let's also try decoding as little-endian for comparison
decoded_value_little_endian = struct.unpack('<d', float_bytes)[0]

print(f"Big-endian decoded value: {decoded_value_big_endian}")
print(f"Little-endian decoded value: {decoded_value_little_endian}")

# Extracting two 4-byte segments
# float_1_bytes = remaining_message[0:4]  # First 4 bytes
# float_2_bytes = remaining_message[4:8]  # Second 4 bytes
#
# # Converting the bytes to float (assuming they're FLOAT_32)
# float_1 = struct.unpack('>f', float_1_bytes)[0]  # Big-endian FLOAT_32
# float_2 = struct.unpack('>f', float_2_bytes)[0]  # Big-endian FLOAT_32
#
# # Print the resulting float values
# print(f"First float (FLOAT_32): {float_1}")
# print(f"Second float (FLOAT_32): {float_2}")
