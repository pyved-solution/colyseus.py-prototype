# ------
# engine-related code, do not modify!
# --------

registry = set()
libname_to_alias_mapping = dict()

def get_alias(origin_lib_name):
    return libname_to_alias_mapping[origin_lib_name]

def has_registered(origin_lib_name):
    return origin_lib_name in libname_to_alias_mapping

def register_lib(alias, libname, value):  # handy for dependency injection
    global registry, libname_to_alias_mapping
    libname_to_alias_mapping[libname] = alias
    if alias in registry:
        raise KeyError(f'Cannot register lib "{alias}" more than once!')
    globals()[alias] = value
    registry.add(alias)


# ------
# custom code the gamedev added
# --------
BG_COLOR = '#b6d53c'

blocks_pop = None
prev_time_info = None
end_game_label = None  # != None means player cannot move bc he/she lost

# (Size of break-out blocks)
BLOCK_W = 54
BLOCK_H = 30
BLOCK_SPACING = 2
SCR_WIDTH = 960
SCR_HEIGHT = 720
LIMIT = SCR_WIDTH / (BLOCK_W + BLOCK_SPACING)
WALL_X, WALL_Y = 4, 80

# physics
PL_WIDTH, PL_HEIGHT = 110, 25
PLAYER_SPEED = 220
MAX_XSPEED_BALL = 225.0
YSPEED_BALL = 288.0

# ball-related
BALL_INIT_POS = 480, 277
BALL_SIZE = 22
