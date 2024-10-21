import msgpack

# Read the binary file produced by notepack.io
FILEN = 'from-js-dump-data/packed.bin'
with open(FILEN, 'rb') as f:
    packed_data = f.read()

try:
   
    print(f'Data found in "{FILEN}" is being de-serialized...')
    unpacked_data = msgpack.unpackb(packed_data, strict_map_key=False)
    print()
    print('Success!')
    print("result=")
    print(unpacked_data)

except Exception as e:
    print(f"Error while deserializing data! {e}")
