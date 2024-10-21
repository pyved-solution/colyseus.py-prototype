class PlayerState:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
        }

    def update(self, update_dict):
        if 'x' in update_dict:
            self.x = update_dict['x']
        if 'y' in update_dict:
            self.y = update_dict['y']
        if 'name' in update_dict:
            self.name = update_dict['name']

class GameState:
    def __init__(self):
        self.players = {}

    def add_player(self, player_id, player_state):
        self.players[player_id] = player_state

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]

    def update_player(self, player_id, update_dict):
        if player_id in self.players:
            self.players[player_id].update(update_dict)

    def to_dict(self):
        return {
            "players": {player_id: player_state.to_dict() for player_id, player_state in self.players.items()}
        }
