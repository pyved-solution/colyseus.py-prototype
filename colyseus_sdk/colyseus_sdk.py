import struct
import threading

import requests
import websocket

from .schema import MutableDataChunk, Schema
from .homemade_deserializer.full_decode import extract_first_fields, Protocol


protocol_state = client = None


class ProtocolSt:
    def __init__(self):
        self.has_joined = False
        self.reconnection_token = None
        self.serializer_id = None
        self.mutable_data = None
        self.join_room_ack_done = False


def init_client(server_url, room_name):
    global protocol_state, client
    protocol_state = ProtocolSt()
    client = ColyseusClient(server_url=server_url, room_name=room_name)


class ColyseusClient:
    def __init__(self, server_url, room_name):
        self.server_url = server_url
        self.room_name = room_name
        self.ws = None

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
        global protocol_state
        # This method handles binary data
        print('debug:binary data reception')
        if data_type == websocket.ABNF.OPCODE_BINARY:
            # Deserialize the binary data properly
            # deserialized_data = deserialize_binary_data(data)

            if self.initial_state_received:
                # Handle incremental updates
                print("Delta update received:", data)
                self.apply_delta_update(data)
            else:  # msg initial, Handle 1st message
                self.initial_state_received = True
                print("Initial room state(raw):", data)

                # process the 1st message
                print('MessageZero>received>> processing ..........')
                session, serializer, offset_nxt_chunk = extract_first_fields(data)
                print('interpretation 1er msg:' , session, serializer, offset_nxt_chunk )

                my_sch = Schema.modelize_from_data(data[offset_nxt_chunk:])
                # TODO - controle d'erreur si les valeurs par défaut sont pas toutes données p/r au schéma
                # TODO - s'assurer que cest bien comme ca qu'on map 0x80 0x81 0x82 etc.
                # sur les variables fournies en début de communication
                protocol_state.mutable_data = MutableDataChunk(my_sch, {
                    "x": 0, "y": 0, "tick": 0,
                    "mapWidth": 0,
                    "mapHeight": 0
                })

                # Send ack  to the server!
                self.acknowledge_initial_state()

                # session, serializer, offset_nxt_chunk = extract_first_fields(data)
                # nxt_chunk = data[offset_nxt_chunk:]
                # self.initial_state_received = True
                # SchemaDeserializer.load(
                #     nxt_chunk, self.fetched_state
                # )
                # room_schema = schema.Schema()
                # for var, schema_s_type in self.fetched_state.items():
                #     room_schema.add_field(var, schema_s_type)
                #     print(var, schema_s_type)
                # self.state = room_schema

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

    def push_data(self, bytes_li:list):
        print('data before packing is:', bytes_li)
        payload = struct.pack('<' + 'B' * len(bytes_li), *bytes_li)
        print()
        #print(payload)

        #payload = [Protocol.ROOM_DATA_BYTES,]
        #payload.extend(uint8_li)
        #uint8_li[0] = Protocol.ROOM_DATA_BYTES
        #payload = uint8_li

        #y = bytes(various_data)
        # struct.pack('!H', various_data[0])
        print('gonna push to ws:',payload)
        self.ws.send(
            payload,
            websocket.ABNF.OPCODE_BINARY  #omg ! forget this line and you are DOOMED
        )

    def apply_delta_update(self, delta):
        # dummy method for logic to apply the delta to the current state
        # In practice, you would need to update the existing state based on the changes in `delta`
        # In other words, the goal of current method is: apply delta change to the existing game state
        protocol_state.mutable_data.apply_delta(
            delta
        )

    def disconnect(self):
        self.ws.close()
