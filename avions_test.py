import logging
import colyseus_sdk
from engine_integration import *


logging.basicConfig(format="%(message)s", level=logging.DEBUG)
# Example: Import or implement a suitable deserialization method here.
# You'll need a way to interpret the binary Schema data.
# This can be replaced by an actual deserializer compatible with Colyseus Schema.


HOST, PORT = 'localhost', 2567
game_engine = GameEngine(
    colyseus_sdk  # dependency injection
)
game_engine.init((HOST, PORT))
# Start the game loop
game_engine.game_loop()
