"""
COLYSEUS.PY sdk

My goal is to allow importing this module as a plug-in inside the pyved-engine

author: "moonbak" also known as Thomas
contact: thomas.iw@kata.games
"""

__version__ = '0.1'


from . import colyseus_sdk
from .colyseus_sdk import init_client


def get_client():
    return colyseus_sdk.client


import time


class PseudoGameEngine:
    def __init__(self, link_to_colyseus):
        # self.game_state = GameState()
        self.game_state = None
        self.colyseus_sdk = link_to_colyseus
        self.player_id = None

    def is_data_available(self):
        # need to do this because the schema/mutable data isnt sync until the first reply
        # has been read from WS (incoming msg from colyseus server)
        return colyseus_sdk.client.initial_state_received

    def mdata_peek(self):
        return colyseus_sdk.protocol_state.mutable_data

    def init(self, netwinfos):
        lib_ref = self.colyseus_sdk
        # Step 0 create the py client
        lib_ref.init_client("http://{}:{}".format(*netwinfos), 'my_room')

        # Step 1: Reserve a seat in the Colyseus room
        reservation_response = lib_ref.get_client().reserve_seat()
        if reservation_response:
            print(reservation_response)
        else:
            raise RuntimeError("Colyseus SDK.client: Failed to reserve a seat.")

        # Step 2: Connect to the Colyseus server
        lib_ref.get_client().connect()

        # if we wait il will crash
        # Wait for the connection to be established
        # time.sleep(1)

        # Step 3: Adding a new player (self)
        self.player_id = "player_1"
        new_player = {"x": 0, "y": 0}  # PlayerState(name="Player 1", x=0, y=0)
        # TODO
        # self.game_state.add_player(self.player_id, new_player)

        # Send initial state to the server
        # TODO first proper msg
        # self.colyseus_client.send(
        #    {"action": "add_player", "player_id": self.player_id, "state": new_player.to_dict()}
        # )

    def game_loop(self):
        player_id = self.player_id
        try:
            while True:
                # Simulate player movement
                # player = self.game_state.players[player_id]
                # player.x += 1
                # player.y += 1

                # Update game state
                # TODO send proper data
                # self.colyseus_client.send(
                #    {"action": "move", "player_id": player_id, "x": player.x, "y": player.y}
                # )

                # Apply updates received from the server
                self.sync_local_state()

                # Wait for a short time to simulate frame duration
                time.sleep(0.1)
        except KeyboardInterrupt:
            # Gracefully disconnect
            self.graceful_exit()

    def graceful_exit(self):
        self.colyseus_sdk.get_client().disconnect()

    def push_data(self, bytes_li):
        self.colyseus_sdk.get_client().push_data(bytes_li)

    def sync_local_state(self):
        # Here, we synchronize game objects state fetched_state ...
        pass
        # for player_id, player_data in colyseus_sdk.client.state.get("players", {}).items():
        #     if player_id not in self.game_state.players:
        #         # Add new player if not already in state
        #         self.game_state.add_player(player_id, PlayerState(**player_data))
        #     else:
        #         # Update existing player state
        #         self.game_state.update_player(player_id, player_data)
