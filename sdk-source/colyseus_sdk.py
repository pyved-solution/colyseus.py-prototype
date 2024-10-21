import websocket
import json
import threading
import requests


# Example: Import or implement a suitable deserialization method here.
# You'll need a way to interpret the binary Schema data.
# This can be replaced by an actual deserializer compatible with Colyseus Schema.
import colyseus_protocol


def deserialize_schema_data(data):
    # Placeholder for deserialization logic
    # Example: Interpret the data to reconstruct the game state
    # You might need a specific protocol to interpret the incoming bytes correctly
    return {"placeholder_key": "deserialized_value"}


class ColyseusClient:
    def __init__(self, server_url, room_name):
        self.server_url = server_url
        self.room_name = room_name
        self.ws = None
        self.state = {}
        self.session_id = None
        self.room_id = None

        self.initial_state_received = False

    def reserve_seat(self):
        # Step 1: Reserve a seat in the room via REST API
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

    # ------------------------
    #  lundi matin le 21/10
    # ------------------------
    def on_open(self, ws):
        print(f"Connected to room: {self.room_id}")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed")

    # def on_message(self, ws, message):
    #     print('debug:msg reception')
    #     try:
    #         update = json.loads(message)
    #         self.handle_state_update(update)
    #     except json.JSONDecodeError:
    #         print("Received non-UTF-8 data; possibly binary message.")

    def on_data(self, ws, data, data_type, continue_flag):
        # This method handles binary data
        print('debug:binary data reception')
        if data_type == websocket.ABNF.OPCODE_BINARY:
            # (for info)
            print("---Raw data---")
            print(data)
            colyseus_protocol.handle_protocol_msg(data, ws)

            # bricolage:
            # deserialized_data = deserialize_schema_data(data)

            # if not self.initial_state_received:
            #     # Handle initial state setup
            #     print("Initial room state received:", deserialized_data)
            #     self.handle_state_sync(deserialized_data)
            #     self.initial_state_received = True
            # else:
            #     # Handle incremental updates
            #     print("Delta update received:", deserialized_data)
            #     self.apply_delta_update(deserialized_data)

            # Further processing would go here to properly decode the binary data

    def send(self, data):
        self.ws.send(json.dumps(data))

    def disconnect(self):
        print('client:websocket connection closes')
        self.ws.close()

    # ---------------------------------
    #  manage local state sync
    # ---------------------------------
    def handle_state_sync(self, update):
        print(f"Received payload for init sync: {update}")
        self.state.update(update)  # For now, as i don't know how to do,
        # we simply update the state directly
        # Send acknowledgment to the server
        self.acknowledge_initial_state()

    def acknowledge_initial_state(self):
        # Send a message to the server acknowledging that we have received the initial state.
        # This might be required for the server to start sending delta updates.
        # The exact format of the acknowledgment message may vary.
        ack_message = {
            "action": "acknowledge_state",
            "sessionId": self.session_id
        }
        self.send(ack_message)
        print("Acknowledgment for initial state sent.")

    def apply_delta_update(self, delta):
        # This method applies delta changes to the existing state
        print(f"Applying delta update: {delta}")
        # Placeholder for logic to apply the delta to the current state
        # In practice, you would need to update the existing state based on the changes in `delta`
        self.state.update(delta)  # This is a simplified example
