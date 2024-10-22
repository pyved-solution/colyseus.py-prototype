"""
goal of cracking the format is that:
 - once done -
we will be able to use Schema.

"""
def byte_in_Ax_format(byte_value):
    # Mask the most significant nibble and compare with 0xA0
    return (byte_value & 0xF0) == 0xA0


def extract_lowvalue_bits(byte_value):
    return 0x0F & byte_value


def interpret_seq(data: bytes, unpacked_obj, initial_values=False):
    offset = 0
    field_marker = data[offset]
    if field_marker not in (0x80, 0x81):
        raise ValueError('unknown start byte!', hex(field_marker))

    if field_marker == 0x81:
        print(' pattern [0x81 0x ??]')

    if field_marker == 0x80 and not byte_in_Ax_format(data[offset+1]):
        print(' pattern [0x80 nn ]')

    str_reading_mode = None
    read_str = ''
    the_pair = []
    info_msg = False
    offset += 1

    # If interpreting initial values, handle raw data
    if initial_values:
        print(f'Interpreting initial value sequence: {data.hex()}')
        # For example, read as integer or string (you may need to adjust this)
        while offset < len(data):
            value = data[offset]
            print(f'Byte {offset}: {hex(value)} interpreted as raw data')
            unpacked_obj[f'initial_value_{offset}'] = value  # Example storing as raw
            offset += 1
        return

    while offset < len(data):
        if str_reading_mode is None:
            if byte_in_Ax_format(data[offset]):
                if not info_msg:
                    print('  pattern [0x80 0xA?] has been found -> varname to type declaration')
                    info_msg = True
                str_reading_mode = extract_lowvalue_bits(data[offset])
        else:
            # print(str_reading_mode)
            if str_reading_mode > 0:
                read_str += chr(data[offset])
            str_reading_mode -= 1
            if str_reading_mode == 0:
                the_pair.append(read_str)
                read_str = ''
                str_reading_mode = None
        offset += 1

    k = len(the_pair)
    if k == 2:
        unpacked_obj[the_pair[0]] = the_pair[1]
    elif k > 0:
        print('warning:read str but no variable<>type pair found')


def split_bytes_by_rank(li_bytes: bytes):
    rez = list()
    current_sequence = bytearray()
    i = 0
    while i < len(li_bytes):
        if li_bytes[i] == 0xFF:  # Detect the rank marker
            if current_sequence:  # Save the previous sequence if exists
                rez.append(bytes(current_sequence))
                current_sequence = bytearray()  # Start a new sequence
            i += 1  # Move to the rank byte (e.g., 0x01, 0x02, etc.)
        else:
            # Accumulate bytes into the current sequence
            current_sequence.append(li_bytes[i])
        i += 1
    # Append the last sequence if there are any remaining bytes
    if current_sequence:
        rez.append(bytes(current_sequence))
    return rez


# ------------------
#  main
# ------------------

data_to_crack = [
    0x80, 0x1, 0x81, 0x1, 0xff, 0x1, 0x80, 0x0, 0x2, 0x80, 0x1, 0x3, 0xff,
    0x2, 0x81, 0x4, 0x80, 0x0, 0xff, 0x3, 0x81, 0x5, 0x80, 0x1, 0xff, 0x4,
    0x80, 0x0, 0x6, 0x80, 0x1, 0x7, 0x80, 0x2, 0x8, 0xff, 0x5, 0x80, 0x0,
    0x9, 0x80, 0x1, 0xa, 0x80, 0x2, 0xb, 0xff, 0x6, 0x80, 0xa1, 0x78, 0x81,
    0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0x7, 0x80, 0xa1, 0x79,
    0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0x8, 0x80, 0xa4,
    0x74, 0x69, 0x63, 0x6b, 0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72,
    0xff, 0x9, 0x80, 0xa8, 0x6d, 0x61, 0x70, 0x57, 0x69, 0x64, 0x74, 0x68,
    0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0xa, 0x80, 0xa9,
    0x6d, 0x61, 0x70, 0x48, 0x65, 0x69, 0x67, 0x68, 0x74, 0x81, 0xa6, 0x6e,
    0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0xb, 0x80, 0xa7, 0x70, 0x6c, 0x61,
    0x79, 0x65, 0x72, 0x73, 0x82, 0x0, 0x81, 0xa3, 0x6d, 0x61, 0x70
]
# An alternative form is (12 sequences), ranks 0 to 11:

# b'\x80\x01\x81\x01\xFF
# \x01\x80\x00\x02\x80\x01\x03\xFF
# \x02\x81\x04\x80\x00\xFF
# \x03\x81\x05\x80\x01\xFF
# \x04\x80\x00\x06\x80\x01\x07\x80\x02\x08\xFF
# \x05\x80\x00\t\x80\x01\n\x80\x02\x0b\xFF
# \x06\x80\xa1x\x81\xa6number\xFF
# \x07\x80\xa1y\x81\xa6number\xFF
# \x08\x80\xa4tick\x81\xa6number\xFF
# \t\x80\xa8mapWidth\x81\xa6number\xFF
# \n\x80\xa9mapHeight\x81\xa6number\xFF
# \x0b\x80\xa7players\x82\x00\x81\xa3map'

import schema
basic_schema = {}

all_seq = split_bytes_by_rank(data_to_crack)

# STEP1 : extract all pairs variable,type
for binary_str_seq in all_seq:
    interpret_seq(binary_str_seq, basic_schema)
print('basic schema found:')
print(basic_schema)
print('-'*48)

# STEP2 : modelize
res_schema = schema.Schema()
for k, ftype in basic_schema.items():
    res_schema.add_field(k, ftype)
print(res_schema)

# essai d'application de deltas
exemple_deltas = [
    b'\x0f\xff\x10\x80\xcb\xf8z\xb6\x1fb\x80\x80@\x81\xcb2y\xe7\xe2\xdb\x88}@',
    b'\x0f\xff\x10\x80\xcb\xf8z\xb6\x1fb\xa0\x80@\x81\xcb2y\xe7\xe2\xdbH}@',
    b'\x0f\xff\x01\x80\x0e\xa99q1PrZeJQ\x10\xff\x10\x80\xcb\xf0\xf5l?\xc4\x80y@\x81\xcb\x99\xbcs\xf1m4\x80@',
    b'\x0f\xff\x01\x80\x0c\xa9y1ezx81qP\x0e\xff\x0e\x80\xcb\x93\xe9\x96d\x0e\xdff@\x81\xcb>\xabF\xbb\xd7\xa9y@',
    b'\x0f\xff\x01@\x00',
    b'\x0f\xff\x01\x80\r\xa9fC4M120vK\x0f\xff\x0f\x80\xcb\xc0\x8c\x89\x99v\xbao@\x81\xcbu\x18\xd7Tz\x03y@'
]

tmp = res_schema.apply_delta(exemple_deltas[5], res_schema.curr_data)

#interpret_seq(data_to_crack, unpacked, True)
#print('unpacked:')
#print(unpacked)
