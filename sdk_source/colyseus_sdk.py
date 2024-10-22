import json
import threading
import struct
import requests
import websocket

from .elements import Protocol, SchemaDeserializer

import logging
logging.basicConfig(format="%(message)s", level=logging.DEBUG )

# Example: Import or implement a suitable deserialization method here.
# You'll need a way to interpret the binary Schema data.
# This can be replaced by an actual deserializer compatible with Colyseus Schema.


class ProtocolSt:
    def __init__(self):
        self.has_joined = False
        self.reconnection_token = None
        self.serializer_id = None
        self.schema_def = {}
        self.join_room_ack_done = False


protocol_state = ProtocolSt()
client = None


def init_client(server_url, room_name):
    global client
    client = ColyseusClient(server_url=server_url, room_name=room_name)


def deserialize_schema_data(data):
    # Placeholder for deserialization logic
    # Example: Interpret the data to reconstruct the game state
    # You might need a specific protocol to interpret the incoming bytes correctly
    return {"placeholder_key": "deserialized_value"}


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

        length = buffer[offset]  # The length of reconnection token (or relevant field)
        print('   (length)', length)
        offset += 1

        reconnection_token = buffer[offset:offset + length].decode("utf-8")
        print('   (reconnection_token)', protocol_state.reconnection_token)
        offset += length

        serializer_id_length = buffer[offset]
        offset += 1
        print('   (serializer_id_len)', serializer_id_length)

        serializer_id = buffer[offset:offset + serializer_id_length].decode("utf-8")
        offset += serializer_id_length
        print('   (serializer)', protocol_state.serializer_id)

        # Assuming that the remaining data is what you need to deserialize
        print('proceeding to decode the rest of the msg...')
        return reconnection_token, serializer_id, offset


from . import schema


class ColyseusClient:
    # def __init__(self, server_url, room_name):
    #     self.server_url = server_url
    #     self.room_name = room_name
    #     self.ws = None
    #     self.state = {}
    #     self.session_id = None
    #     self.room_id = None
    #
    #     self.initial_state_received = False

    def __init__(self, server_url, room_name):
        self.server_url = server_url
        self.room_name = room_name
        self.ws = None

        self.fetched_state = {}

        self.session_id = None
        self.room_id = None
        self.initial_state_received = False

    def reserve_seat(self):
        # Step 1: Reserve a seat in the room via REST API
        print('join or create room called...')

        url = f"{self.server_url}/matchmake/joinOrCreate/{self.room_name}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {}  # Colyseus expects at least an empty JSON body
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()
            self.session_id = response_data.get("sessionId")
            self.room_id = response_data.get("room", {}).get("roomId")
            print('reservation seems fine, session;roomId pair=', self.session_id, self.room_id)
            return response_data
        except requests.RequestException as e:
            print(f"Error reserving seat: {e}")
            return None

    # version1
    # Step 2: Use seat reservation information to establish WebSocket connection
    # def connect(self):
    #     if not self.session_id or not self.room_id:
    #         raise Exception("Something is wrong with seat reservation? Have you done the reservation?")
    #     ws_url = f"{self.server_url.replace('http', 'ws')}/{self.room_id}?sessionId={self.session_id}"
    #     self.ws = websocket.WebSocketApp(
    #         ws_url,
    #         on_open=self.on_open,
    #         on_message=self.on_message,
    #         on_error=self.on_error,
    #         on_close=self.on_close
    #     )
    #     wst = threading.Thread(target=self.ws.run_forever)
    #     wst.daemon = True
    #     wst.start()

    def connect(self):
        # Step 2: Use seat reservation information to establish WebSocket connection
        if not self.session_id or not self.room_id:
            raise Exception("Seat reservation is required before connecting.")

        # Immediately use the seat reservation details to connect
        ws_url = f"{self.server_url.replace('http', 'ws')}/matchmake/{self.room_id}?sessionId={self.session_id}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self.on_open,
            # on_message=self.on_message,  # This will handle only text messages
            on_error=self.on_error,
            on_close=self.on_close,
            on_data=self.on_data  # This will handle binary messages
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def on_open(self, ws):
        print(f"Connected to room: {self.room_id}")

    def on_data(self, ws, data, data_type, continue_flag):
        # This method handles binary data
        print('debug:binary data reception')
        if data_type == websocket.ABNF.OPCODE_BINARY:
            # Deserialize the binary data properly
            # deserialized_data = deserialize_binary_data(data)

            if not self.initial_state_received:  # msg initial, Handle 1st message
                print("Initial room state(raw):", data)
                session, serializer, offset_nxt_chunk = extract_first_fields(data)
                nxt_chunk = data[offset_nxt_chunk:]

                # self.handle_state_update(deserialized_data)
                self.initial_state_received = True
                SchemaDeserializer.load(
                    nxt_chunk, self.fetched_state
                )
                room_schema = schema.Schema()
                for var, schema_s_type in self.fetched_state.items():
                    room_schema.add_field(var, schema_s_type)
                    print(var, schema_s_type)

                self.state = room_schema

                # Send the acknowledgment to the server!
                self.acknowledge_initial_state()

            else:
                #raise NotImplementedError('only msg1 can be read')
                # Handle incremental updates
                print("Delta update received:", data)
                self.apply_delta_update(data)

                #self.apply_delta_update(deserialized_data)

    # Send a binary or text message back to the server to confirm that you received the initial state
    # The exact format of the acknowledgment depends on Colyseus protocol
    # Example: Send an acknowledgment message to continue receiving delta updates
    def acknowledge_initial_state(self):
        ack_message = struct.pack('>B', Protocol.JOIN_ROOM)  # >B means big-endian, unsigned char for protocol code
        self.ws.send(ack_message, opcode=websocket.ABNF.OPCODE_BINARY)
        print("<_ok_>Acknowledgment for initial state sent.")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    def notify_server(self, various_data):
            print('sendin:')
            y = bytes(various_data)# struct.pack('!H', various_data[0])
            print(y)
            self.ws.send(y)

    def handle_state_update(self, update):
        # This method processes full state changes.
        print(f"Received full state update: {update}")
        # For now, we simply update the state directly
        self.state = update  # Replace entire state with the initial full state

    def apply_delta_update(self, delta):
        # This method applies delta changes to the existing state
        print('DIFF=',self.state.deserialize(delta))

        # Placeholder for logic to apply the delta to the current state
        # In practice, you would need to update the existing state based on the changes in `delta`
        # self.state.update(delta)  # This is a simplified example

    def disconnect(self):
        self.ws.close()
