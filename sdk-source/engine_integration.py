from colyseus_sdk import ColyseusClient
from game_state import GameState, PlayerState
import time


class GameEngine:
    def __init__(self):
        self.game_state = GameState()
        self.colyseus_client = None
        self.player_id = None

    def init(self, netwinfos):
        self.colyseus_client = ColyseusClient(server_url="http://{}:{}".format(*netwinfos), room_name="my_room")

        # Step 1: Reserve a seat in the Colyseus room
        reservation_response = self.colyseus_client.reserve_seat()
        if not reservation_response:
            print("Failed to reserve a seat.")
            return
        print('reservation?', reservation_response)
        # Step 2: Connect to the Colyseus server
        self.colyseus_client.connect()

        # if we wait il will crash
        # Wait for the connection to be established
        # time.sleep(1)

        # Step 3: Adding a new player (self)
        self.player_id = "player_1"
        new_player = PlayerState(name="Player 1", x=0, y=0)
        self.game_state.add_player(self.player_id, new_player)

        # Send initial state to the server
        # TODO first proper msg
        #self.colyseus_client.send(
        #    {"action": "add_player", "player_id": self.player_id, "state": new_player.to_dict()}
        #)

    def game_loop(self):
        player_id = self.player_id
        try:
            while True:
                # Simulate player movement
                player = self.game_state.players[player_id]
                player.x += 1
                player.y += 1

                # Update game state
                # TODO send proper data
                #self.colyseus_client.send(
                #    {"action": "move", "player_id": player_id, "x": player.x, "y": player.y}
                #)

                # Apply updates received from the server
                self.synchronize_state()

                # Wait for a short time to simulate frame duration
                time.sleep(0.1)
        except KeyboardInterrupt:
            # Gracefully disconnect
            self.colyseus_client.disconnect()

    def synchronize_state(self):
        # Here, we synchronize state using received data
        for player_id, player_data in self.colyseus_client.state.get("players", {}).items():
            if player_id not in self.game_state.players:
                # Add new player if not already in state
                self.game_state.add_player(player_id, PlayerState(**player_data))
            else:
                # Update existing player state
                self.game_state.update_player(player_id, player_data)


HOST, PORT = 'localhost', 2567


if __name__ == "__main__":
    game_engine = GameEngine()
    game_engine.init((HOST, PORT))
    # Start the game loop
    game_engine.game_loop()
