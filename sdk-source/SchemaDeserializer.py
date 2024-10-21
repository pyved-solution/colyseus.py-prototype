import struct


class FieldType:
    END_OF_STRUCTURE = 0xC1,  # (msgpack spec: never used)
    NIL = 0xC0,
    INDEX_CHANGE = 0xD4,
    FLOAT_32 = 0xCA,
    FLOAT_64 = 0xCB,
    U_INT_8 = 0xCC,
    U_INT_16 = 0xCD,
    U_INT_32 = 0xCE,
    U_INT_64 = 0xCF

    # {
    #     // uint 64
    #     return (varint_t) decodeUint64(bytes, it);
    # }
    # else if (prefix == 0xd0)
    # {
    #     // int 8
    #     return (varint_t) decodeInt8(bytes, it);
    # }
    # else if (prefix == 0xd1)
    # {
    #     // int 16
    #     return (varint_t) decodeInt16(bytes, it);
    # }
    # else if (prefix == 0xd2)
    # {
    #     // int 32
    #     return (varint_t) decodeInt32(bytes, it);
    # }
    # else if (prefix == 0xd3)
    # {
    #     // int 64
    #     return (varint_t) decodeInt64(bytes, it);
    # }
    # else if (prefix > 0xdf)
    # {
    #     // negative fixint
    #     return (varint_t) ((0xff - prefix + 1) * -1);
    # }


class SchemaDeserializer:
    def __init__(self):
        pass

    def deserialize(self, data):
        print('schema DESERIALIZED called')
        offset = 0
        state = {}

        while offset < len(data):
            field_type = data[offset]
            offset += 1

            if field_type == 0x80:  # Example: Handle an empty map (schema marker)
                state['empty_map'] = {}

            elif field_type == FieldType.U_INT_16:  # Example: Handle unsigned 16-bit integer
                (value,) = struct.unpack_from(">H", data, offset)
                offset += 2
                state['unsigned_16'] = value

            elif field_type == 0x81:  # Handle a basic single-value map
                map_key_length = data[offset]
                offset += 1
                print('mapkey len:', map_key_length)
                print(data[offset:offset + map_key_length])
                map_key = data[offset:offset + map_key_length].decode('utf-8')
                offset += map_key_length

                # Assume next byte represents the value
                map_value = data[offset]
                offset += 1
                state[map_key] = map_value

            elif field_type == 0xa1:  # Assuming it's a string type
                str_length = data[offset]
                offset += 1
                print('str len=', str_length)
                try:
                    value = data[offset:offset + str_length].decode('utf-8')
                except UnicodeDecodeError:
                    value = "???_hint_Invalid_utf8_encoding"
                offset += str_length
                state['string_value'] = value

            else:
                # field_type == 0xff:  # Placeholder for end marker or similar
                pass  # Skip for now, no action needed for `0xff`

            # TODO: add further handlers for other supported data types

        return state


# -------------
# test 2
# --------------
import struct
from schema_MyRoomState import Player, MyRoomState


def decode_player(data: bytes):
    # Unpacking the binary data for a Player
    # Assuming the format is [float (x), float (y), int (tick)]
    x, y, tick = struct.unpack('ffI', data[:12])  # float, float, int (12 bytes total)
    return Player(x, y, tick)


# Helper function to decode a variable-length string
def decode_string(data: bytes, offset: int):
    str_len = data[offset]
    # Check if the string is in small format (0xa0 + length)
    first_byte = data[offset]
    offset += 1
    if 0xa0 <= first_byte <= 0xbf:
        length = first_byte - 0xa0
        string = data[offset:offset + length].decode('utf-8')
        offset += length
    else:
        raise ValueError(f"Unexpected string prefix: {hex(first_byte)}")

    return string, offset


# Helper function to decode a number (float or int)
def decode_number(data: bytes, offset: int):
    num_type = data[offset]
    offset += 1

    if num_type == 0xca:  # 0xca represents a 32-bit float
        number = struct.unpack('>f', data[offset:offset + 4])[0]  # Big-endian float
        offset += 4
    elif num_type == 0xcc:  # 0xcc represents an 8-bit unsigned int
        number = struct.unpack('B', data[offset:offset + 1])[0]
        offset += 1
    elif num_type == 0xcd:  # 0xcd represents a 16-bit unsigned int
        number = struct.unpack('>H', data[offset:offset + 2])[0]  # Big-endian 16-bit int
        offset += 2
    else:
        raise ValueError(f"Unknown number type: {num_type}")

    return number, offset


# Helper function to decode a player object
def decode_player(data: bytes, offset: int):
    x, offset = decode_number(data, offset)
    y, offset = decode_number(data, offset)
    tick, offset = decode_number(data, offset)
    return Player(x, y, tick), offset


# Function to decode the entire room state
def decode_room_state(data: bytes):
    state = MyRoomState()
    offset = 0

    while offset < len(data):
        field_marker = data[offset]
        print('  marker={}'.format(hex(field_marker)))
        offset += 1

        if field_marker == 0x80:  # Start of a new key
            key, offset = decode_string(data, offset)

            if key == "mapWidth":
                state.mapWidth, offset = decode_number(data, offset)
                print('mapwidth found:', state.mapWidth)
            elif key == "mapHeight":
                state.mapHeight, offset = decode_number(data, offset)
                print('mapheight found:', state.mapHeight)
            elif key == "players":
                # Players are encoded... ? as a map
                _, offset = decode_string(data, offset)  # to skip the 'map' identifier
                num_players = data[offset]
                print('nam_player:', data[offset])
                offset += 1

                for _ in range(num_players):
                    player_id, offset = decode_string(data, offset)
                    player, offset = decode_player(data, offset)
                    state.players[player_id] = player

        elif field_marker == 0x81:
            continue

        else:
            raise ValueError(f"Unexpected field marker: {field_marker}")

    return state


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


def interpret_seq(data: bytes):
    field_marker = data[0]
    offset = 1

    number = None
    if field_marker == 0xCA:  # 0xca represents a 32-bit float
        number = struct.unpack('>f', data[offset:offset + 4])[0]  # Big-endian float
        offset += 4
    elif field_marker == 0xCC:  # 0xcc represents an 8-bit unsigned int
        number = struct.unpack('B', data[offset:offset + 1])[0]
        offset += 1
    elif field_marker == 0xCD:  # 0xcd represents a 16-bit unsigned int
        number = struct.unpack('>H', data[offset:offset + 2])[0]  # Big-endian 16-bit int
        offset += 2
    elif field_marker == 0x80:
        number = utf8_read(data, offset)

    if number:
        return number
    else:
        print('cant decode for field_marker:', hex(field_marker))
        # ValueError(f"Unknown number type: {num_type}")


# def xx_decode_player(data: bytes, offset: int):
#     # Assuming player data has x, y, tick in sequence (all as numbers)
#     x, offset = decode_number(data, offset)
#     y, offset = decode_number(data, offset)
#     tick, offset = decode_number(data, offset)
#     return Player(x, y, tick), offset
#
#
# def xx_decode_room_state(data: bytes):
#     # Initialize default values
#     state = MyRoomState(mapWidth=0, mapHeight=0)
#     offset = 0
#
#     # Decoding loop
#     while offset < len(data):
#         key, offset = decode_string(data, offset)
#         if key == "mapWidth":
#             state.mapWidth, offset = decode_number(data, offset)
#             print(state.mapWidth)
#         elif key == "mapHeight":
#             state.mapHeight, offset = decode_number(data, offset)
#         elif key == "players":
#             _, offset = decode_string(data, offset)  # Skip the type of the map (e.g., 'map')
#             num_players = data[offset]  # Get the number of players
#             offset += 1
#             for _ in range(num_players):
#                 player_id, offset = decode_string(data, offset)
#                 player, offset = decode_player(data, offset)
#                 state.players[player_id] = player
#     return state


def utf8_read(view, offset):
    length = view[offset]
    offset += 1
    string = ""
    my_chr = 0

    i = offset
    end = offset + length

    while i < end:
        byte = view[i]
        i += 1

        if (byte & 0x80) == 0x00:
            string += chr(byte)
            continue

        if (byte & 0xe0) == 0xc0:
            string += chr(
                ((byte & 0x1f) << 6) |
                (view[i] & 0x3f)
            )
            i += 1
            continue

        if (byte & 0xf0) == 0xe0:
            string += chr(
                ((byte & 0x0f) << 12) |
                ((view[i] & 0x3f) << 6) |
                ((view[i + 1] & 0x3f) << 0)
            )
            i += 2
            continue

        if (byte & 0xf8) == 0xf0:
            my_chr = ((byte & 0x07) << 18) | ((view[i] & 0x3f) << 12) | ((view[i + 1] & 0x3f) << 6) | (
                        view[i + 2] & 0x3f)
            i += 3
            if my_chr >= 0x010000:
                my_chr -= 0x010000
                string += chr((my_chr >> 10) + 0xD800) + chr((my_chr & 0x3FF) + 0xDC00)
            else:
                string += chr(my_chr)
            continue

        raise ValueError(f"Invalid byte {hex(byte)}")
    return string


if __name__ == '__main__':
    # Example usage
    # schema_definition = {}  # Define your schema here as a reference if needed
    # deserializer = SchemaDeserializer()
    raw_data = b'\x80\x01\x81\x01\xff\x01\x80\x00\x02\x80\x01\x03\xff\x02\x81\x04\x80\x00\xff\x03\x81\x05\x80\x01\xff\x04\x80\x00\x06\x80\x01\x07\x80\x02\x08\xff\x05\x80\x00\t\x80\x01\n\x80\x02\x0b\xff\x06\x80\xa1x\x81\xa6number\xff\x07\x80\xa1y\x81\xa6number\xff\x08\x80\xa4tick\x81\xa6number\xff\t\x80\xa8mapWidth\x81\xa6number\xff\n\x80\xa9mapHeight\x81\xa6number\xff\x0b\x80\xa7players\x82\x00\x81\xa3map'
    print(raw_data)
    # deserialized_state = deserializer.deserialize(raw_data)
    # print(deserialized_state)

    all_seq = split_bytes_by_rank(raw_data)
    print('nb seq=', len(all_seq))
    for one_seq in all_seq:
        print(one_seq)
        print(interpret_seq(one_seq))

    print('exit prog')
