"""
contient un call vers Schema.from_binary_description(...)
"""

import schema

# Create a new schema
player_schema = schema.Schema()
# player_schema.add_field("x", "float")
# player_schema.add_field("y", "float")
# player_schema.add_field("name", "string")

# Example binary data (could be received from the server)
binary_data = b'\x43\x96\x00\x00\x43\x97\x33\x33\x05hello'  # x = 300, y = 305.2, name = "hello"

bin_data = b'\x80\x01\x81\x01\xff\x01\x80\x00\x02\x80\x01\x03\xff\x02\x81\x04\x80\x00\xff\x03\x81\x05\x80\x01\xff\x04\x80\x00\x06\x80\x01\x07\x80\x02\x08\xff\x05\x80\x00\t\x80\x01\n\x80\x02\x0b\xff\x06\x80\xa1x\x81\xa6number\xff\x07\x80\xa1y\x81\xa6number\xff\x08\x80\xa4tick\x81\xa6number\xff\t\x80\xa8mapWidth\x81\xa6number\xff\n\x80\xa9mapHeight\x81\xa6number\xff\x0b\x80\xa7players\x82\x00\x81\xa3map'

player_schema.from_binary_description(bin_data)
print(player_schema)
from sys import exit
exit(0)

# Now, as a tests let's deserialize & output some data
# Expected result is: {'x': 300.0, 'y': 305.2, 'name': 'hello'}
deserialized_data = player_schema.deserialize(binary_data)
print(deserialized_data)

# Example binary description: 3 fields (name="x" type=float, name="y" type=float, name="name" type=string)
binary_description = b'\x03\x01x\x02\x01y\x02\x04name\x03'

# Initial state received from server (x=300, y=400, name="player1")
binary_data = b'\x43\x96\x00\x00\x43\xc8\x00\x00\x07player1'
state = schema.deserialize(binary_data)
print("Initial state:", state)

# Delta update: only x changes to 350.5
delta_data = b'\x01x\x02\x43\x9c\x00\x00'  # (x changes to 350.5)
state = schema.apply_delta(delta_data, state)
print("Updated state:", state)
