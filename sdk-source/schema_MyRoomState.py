from typing import Dict, List

class InputData:
    def __init__(self, left: bool = False, right: bool = False, up: bool = False, down: bool = False, tick: int = 0):
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.tick = tick

class Player:
    def __init__(self, x: float = 0.0, y: float = 0.0, tick: int = 0):
        self.x = x
        self.y = y
        self.tick = tick
        self.inputQueue: List[InputData] = []

class MyRoomState:
    def __init__(self, mapWidth: int = 0, mapHeight: int = 0):
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight
        self.players: Dict[str, Player] = {}
