"""
goal of cracking the format is that:
 - once done -
we will be able to use Schema.

"""


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


def byte_in_Ax_format(byte_value):
    # Mask the most significant nibble and compare with 0xA0
    return (byte_value & 0xF0) == 0xA0


def extract_lowvalue_bits(byte_value):
    return 0x0F & byte_value


def interpret_seq(data: bytes, unpacked_obj, var_order: list, initial_values=False):
    offset = 0
    field_marker = data[offset]
    if field_marker not in (0x80, 0x81):
        raise ValueError('unknown start byte!', hex(field_marker))

    if field_marker == 0x81:
        print(' pattern [0x81 0x ??]')

    if field_marker == 0x80 and not byte_in_Ax_format(data[offset + 1]):
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
        print(' ___from schema found:', the_pair)
        var_order.append(the_pair[0])
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


def extract_first_fields(buffer):
    """
    :param buffer:
    :return: reconnection_token, serializer_id, offset(when starts the rest of the msg)
    """
    offset = 0
    protocol_code = buffer[offset]
    offset += 1

    if protocol_code == Protocol.JOIN_ROOM:
        """
        typical steps:
        - (A)Read the Reconnection Token and Serializer ID.
        - (B)Instantiate the Serializer: If not already available, the serializer instance is created to manage the state
        - (C)Perform Handshake: If the serializer has a handshake method, it's called to initialize
        - (D)Mark Room as Joined:
           - 1 sets hasJoined to true
           - 2 and invokes the onJoin event
        - (E)Acknowledge Room Join: Sends a JOIN_ROOM protocol message back to the server to confirm successful join
        """

        """
        Handling JOIN_ROOM (code 10):
        - Typically, read reconnection token, serializer, etc.
        """
        # length of reconnection token (or relevant field)
        length = buffer[offset]
        offset += 1

        reconnection_token = buffer[offset:offset + length].decode("utf-8")
        offset += length

        serializer_id_length = buffer[offset]
        offset += 1

        serializer_id = buffer[offset:offset + serializer_id_length].decode("utf-8")
        offset += serializer_id_length
        # return the val. offset so elsewere we know what remains to be processed
        return reconnection_token, serializer_id, offset
