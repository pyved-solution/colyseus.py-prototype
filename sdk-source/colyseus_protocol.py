from SchemaDeserializer import SchemaDeserializer


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


class CommsState:
    def __init__(self):
        self.has_joined = False


protocol_state = CommsState()
import msgpack


def handle_protocol_msg(buffer, ref_ws):
    offset = 0
    protocol_code = buffer[offset]
    offset += 1

    def unwrap_remaining(data):  # Deserialize the remaining data using MessagePack
        try:
            rez = msgpack.unpackb(data, strict_map_key=False)
            return rez
        except Exception as e:
            print(f"Error unwrap remaining data state: {e}")

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
        if protocol_code == Protocol.JOIN_ROOM:
            """
            Handling JOIN_ROOM (code 10):
            - Typically, read reconnection token, serializer, etc.
            """
            length = buffer[offset]  # The length of reconnection token (or relevant field)
            print('   (length)', length)
            offset += 1

            reconnection_token = buffer[offset:offset + length].decode("utf-8")
            print('   (reconnection_token)', reconnection_token)
            offset += length

            serializer_id_length = buffer[offset]
            offset += 1
            print('   (serializer_id_len)', serializer_id_length)

            serializer_id = buffer[offset:offset + serializer_id_length].decode("utf-8")
            offset += serializer_id_length
            print('   (serializer)', serializer_id)

            # Assuming that the remaining data is what you need to deserialize
            print('restes:', buffer[offset:])
            deserializer = SchemaDeserializer() #'schema')
            rez = deserializer.deserialize(buffer[offset:])
            print('--->')
            print(rez)

            # remaining_data = buffer[offset:]
            # retour = unwrap_remaining(remaining_data)
            # print(utf8_read(buffer, offset))

            # For now, just set the room as joined and acknowledge
            protocol_state.has_joined = True
            # print('  ', retour)

            # Acknowledge joining the room to start syncing
            ref_ws.send(bytes([Protocol.JOIN_ROOM]))

    elif protocol_code == Protocol.ROOM_STATE:
        print('room state recu [protocol ]..................')
        retour = unwrap_remaining(buffer[offset:])
        print(retour)

        # Read metadata for the room state
        # room_id_length = buffer[offset]
        # je vais decode mais que après l'espace ' ' (=char 0x20)
        # utf8_parsed_msg = buffer[7:].decode("utf-8")
        # print('***', utf8_parsed_msg)

    elif protocol_code == Protocol.ROOM_STATE_PATCH:
        raise NotImplementedError('room state patch not handled!')

    else:
        print(f"Unhandled protocol code: {protocol_code}")

# also broken

# def handle_protocol_msg(buffer, ref_ws):
#     offset = 0
#     protocol_code = buffer[offset]
#     offset += 3
#     if protocol_code == Protocol.JOIN_ROOM:
#         """
#         typical steps:
#         - (A)Read the Reconnection Token and Serializer ID.
#         - (B)Instantiate the Serializer: If not already available, the serializer instance is created to manage the state
#         - (C)Perform Handshake: If the serializer has a handshake method, it's called to initialize
#         - (D)Mark Room as Joined:
#            - 1 sets hasJoined to true
#            - 2 and invokes the onJoin event
#         - (E)Acknowledge Room Join: Sends a JOIN_ROOM protocol message back to the server to confirm successful join
#         """
#         # for now we will just do D1 and E,
#         # because i'm lazy today
#         protocol_state.has_joined = True
#         print('  ', ref_ws)
#         ref_ws.send_bytes([Protocol.JOIN_ROOM])
#
#     elif protocol_code == Protocol.ROOM_STATE:
#         print('room state recu [protocol ]..................')
#         # Read metadata for the room state
#         room_id_length = buffer[offset]
#
#         # je vais decode mais que après l'espace ' ' (=char 0x20)
#
#         utf8_parsed_msg = buffer[7:].decode("utf-8")
#         print('***',utf8_parsed_msg)
#
#         #offset += 1
#
#         #room_id = buffer[offset:offset + room_id_length].decode("utf-8")
#         #offset += room_id_length
#
#         # Now we parse the actual state (serialized in a specific format)
#         # This will depend on the serializer (for example, Schema)
#         # try:
#         #     state_length = struct.unpack(">I", buffer[offset:offset + 4])[0]  # Reading a 4-byte length
#         #     offset += 4
#         #
#         #     state_data = buffer[offset:offset + state_length]
#         #     offset += state_length
#         #
#         #     print(f"Room ID: {room_id}, State Data (length {state_length}): {state_data}")
#         #     # Add further deserialization logic here to fully parse the state data.
#         #
#         # except struct.error:
#         #     print("Failed to unpack state length. Invalid format received.")
#     else:
#         print(f"Unhandled protocol code: {protocol_code}")


# deprec
def xx_handle_protocol_msg(msg_raw_view, ref_ws):
    global protocol_state

    offset = 0
    protocol_code = msg_raw_view[offset]
    print('[protocol] read code=', protocol_code)
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
        # for now we will just do D1 and E,
        # because i'm lazy today
        protocol_state.has_joined = True
        print('  ', ref_ws)
        ref_ws.send_bytes([Protocol.JOIN_ROOM])

    elif protocol_code == Protocol.ROOM_STATE:
        # Handle full room state
        print("[protocol] handle room state: ")
        print(msg_raw_view)
        # state = utf8_read(msg_raw_view, offset)
        # TODO decrypt?
        # You would also need to implement logic to parse this state properly

    elif protocol_code == Protocol.ROOM_STATE_PATCH:
        # Handle room state patch (delta)
        patch = utf8_read(msg_raw_view, offset)
        print(f"[Protocol]Room state patch: {patch}")
        # Again, implement appropriate patching logic to merge with the current state

