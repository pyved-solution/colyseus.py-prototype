import random
from . import glvars


pyv = glvars.pyv
pygame = pyv.pygame


def player_create():
    player = pyv.new_from_archetype('player')
    pyv.init_entity(player, {
        'speed': 0.0,
        'controls': {'left': False, 'right': False},
        'body': pygame.rect.Rect(glvars.SCR_WIDTH//2, 635, glvars.PL_WIDTH, glvars.PL_HEIGHT)
    })


def ball_create():
    ball = pyv.new_from_archetype('ball')
    if random.choice((True, False)):
        # we select the right dir.
        initial_vx = random.uniform(0.33*glvars.MAX_XSPEED_BALL, glvars.MAX_XSPEED_BALL)
    else:
        initial_vx = random.uniform(-glvars.MAX_XSPEED_BALL, -0.33 * glvars.MAX_XSPEED_BALL)
    pyv.init_entity(ball, {
        'speed_X': initial_vx,
        'speed_Y': glvars.YSPEED_BALL,
        'body': pygame.rect.Rect(glvars.BALL_INIT_POS[0], glvars.BALL_INIT_POS[1], glvars.BALL_SIZE, glvars.BALL_SIZE)
    })


def blocks_create():
    bcy = 0
    for column in range(5):
        bcy = bcy + glvars.BLOCK_H + glvars.BLOCK_SPACING
        bcx = -glvars.BLOCK_W
        for row in range(round(glvars.LIMIT)):
            bcx = bcx + glvars.BLOCK_W + glvars.BLOCK_SPACING
            rrect = pygame.rect.Rect(0 + bcx, 0 + bcy, glvars.BLOCK_W, glvars.BLOCK_H)
            pyv.init_entity(pyv.new_from_archetype('block'), {
                'body': rrect
            })
