import binascii

# Read the binary file
with open('msgpack-aller-retour/from-js-dump-data/packed.bin', 'rb') as f:
    packed_data = f.read()

# Convert the data to hexadecimal representation
hex_representation = binascii.hexlify(packed_data)

# Convert hex bytes to a readable format with \x representation
formatted_hex = ''.join(['\\x' + hex_representation[i:i+2].decode('utf-8') for i in range(0, len(hex_representation), 2)])

# Print the formatted representation
print(formatted_hex)
