
class Protocol:
    HANDSHAKE = 9
    JOIN_ROOM = 10
    ERROR = 11
    LEAVE_ROOM = 12
    ROOM_DATA = 13
    ROOM_STATE = 14
    ROOM_STATE_PATCH = 15
    ROOM_DATA_SCHEMA = 16
    ROOM_DATA_BYTES = 17


def split_bytes_by_rank(X: bytes):
    sequences = []
    current_sequence = bytearray()

    i = 0
    while i < len(X):
        if X[i] == 0xFF:  # Detect the rank marker
            if current_sequence:  # Save the previous sequence if exists
                sequences.append(bytes(current_sequence))
                current_sequence = bytearray()  # Start a new sequence

            i += 1  # Move to the rank byte (e.g., 0x01, 0x02, etc.)
        else:
            # Accumulate bytes into the current sequence
            current_sequence.append(X[i])
        i += 1

    # Append the last sequence if there are any remaining bytes
    if current_sequence:
        sequences.append(bytes(current_sequence))
    return sequences


def byte_in_Ax_format(byte_value):
    # Mask the most significant nibble and compare with 0xA0
    return (byte_value & 0xF0) == 0xA0


def extract_lowvalue_bits(byte_value):
    return 0x0F & byte_value


def interpret_seq(data: bytes, unpacked_obj):
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


class SchemaDeserializer:
    def __init__(self):
        pass

    @staticmethod
    def load(bindata, saved_schema):
        all_seq = split_bytes_by_rank(bindata)
        # nombre de sequences : len(all_seq)
        for binary_str_seq in all_seq:
            unpacked = dict()
            interpret_seq(binary_str_seq, unpacked)
            if len(unpacked):
                saved_schema.update(unpacked)

    # - (1st attempt:) KEPT FOR REFERENCE

    # def deserialize(self, data):
    #     print('schema DESERIALIZED called')
    #     offset = 0
    #     state = {}
    #
    #     while offset < len(data):
    #         field_type = data[offset]
    #         offset += 1
    #
    #         if field_type == 0x80:
    #             state['empty_map'] = {}
    #
    #         elif field_type == FieldType.U_INT_16:  # Example: Handle unsigned 16-bit integer
    #             (value,) = struct.unpack_from(">H", data, offset)
    #             offset += 2
    #             state['unsigned_16'] = value
    #
    #         elif field_type == 0x81:  # Handle a basic single-value map
    #             map_key_length = data[offset]
    #             offset += 1
    #             print('mapkey len:', map_key_length)
    #             print(data[offset:offset + map_key_length])
    #             map_key = data[offset:offset + map_key_length].decode('utf-8')
    #             offset += map_key_length
    #
    #             # Assume next byte represents the value
    #             map_value = data[offset]
    #             offset += 1
    #             state[map_key] = map_value
    #
    #         elif field_type == 0xa1:  # Assuming it's a string type
    #             str_length = data[offset]
    #             offset += 1
    #             print('str len=', str_length)
    #             try:
    #                 value = data[offset:offset + str_length].decode('utf-8')
    #             except UnicodeDecodeError:
    #                 value = "???_hint_Invalid_utf8_encoding"
    #             offset += str_length
    #             state['string_value'] = value
    #
    #         else:
    #             # field_type == 0xff:  # Placeholder for end marker or similar
    #             pass  # Skip for now, no action needed for `0xff`
    #         # add further handlers for other supported data types
    #     return state
