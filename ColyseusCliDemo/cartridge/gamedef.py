import time

from . import glvars
from . import systems
from .world import blocks_create, player_create, ball_create
import random

pyv = glvars.pyv
pygame = pyv.pygame
ref_state = None
net_eng = None

import logging


@pyv.declare_begin
def init_game(vmst=None):
    global ref_state, net_eng
    ref_state = MiniState()

    # init net stuff [COLYSEUS] --
    net_eng = glvars.net.PseudoGameEngine(
        glvars.net
    )
    HOST, PORT = 'localhost', 2567
    net_eng.init((HOST, PORT))  # connect via colyseus+WS
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    # --

    pyv.init(0, forced_size=(800, 600), wcaption='colyseus client demo')
    print(pyv.get_surface().get_size())
    # pyv.define_archetype('player', ('body', 'speed', 'controls'))
    # pyv.define_archetype('block', ('body', ))
    # pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))
    # blocks_create()
    # player_create()
    # ball_create()
    # pyv.bulk_add_systems(systems)


class MiniState:
    def __init__(self):
        self.players = {
            0: {'x': random.randint(32, 800 - 32), 'y': random.randint(32, 600 - 32), 'tick': 0},
            1: {'x': 0, 'y': 0, 'tick': 0},
            2: {'x': 0, 'y': 0, 'tick': 0},
        }


import json


def gen_packet_for_direction(direction: str):
    # '0' -> {"left": false, "right": false, "up": false, "down": false}
    """
    left right up down...
    """
    offsetx, offsety = {
        'N': (0, -1),
        'NE': (1, -1),
        'NW': (-1, -1),
        'S': (0, 1),
        'SE': (1, 1),
        'SW': (-1, 1),
        'E': (1, 0),
        'W': (-1, 0),
    }[direction]
    mimic_packet = [
        0x0d, 0x00, 0x84, 0xa4, 0x6c, 0x65, 0x66, 0x74,
        0xc3 if offsetx < 0 else 0xc2,  # c2 = immobile, c3 fera aller a gauche
        0xa5, 0x72, 0x69, 0x67, 0x68, 0x74,
        0xc3 if offsetx > 0 else 0xc2,  # c3 fera aller a droite
        0xa2, 0x75, 0x70,
        0xc3 if offsety < 0 else 0xc2,  # haut / c2==statique
        0xa4, 0x64, 0x6f, 0x77, 0x6e,
        0xc3 if offsety > 0 else 0xc2  # bas
    ]
    return mimic_packet

    # mimic_p = b'\r\x00\x84\xa4left\xc2\xa5right\xc2\xa2up\xc2\xa4down\xc2'
    # data_ints = struct.unpack('<' + 'b' * len(bstr), bstr)


cached_dir = None
cached_packet = None


@pyv.declare_update
def upd(time_info=None):
    global cached_dir, cached_packet

    ev_mger = pyv.get_ev_manager()
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pyv.vars.gameover = True

    active_keys = pygame.key.get_pressed()
    direc = None
    # 8-dir
    if active_keys[pygame.K_LEFT] and active_keys[pygame.K_DOWN]:
        direc = 'SW'
    elif active_keys[pygame.K_LEFT] and active_keys[pygame.K_UP]:
        direc = 'NW'
    elif active_keys[pygame.K_RIGHT] and active_keys[pygame.K_DOWN]:
        direc = 'SE'
    elif active_keys[pygame.K_RIGHT] and active_keys[pygame.K_UP]:
        direc = 'NE'
    elif active_keys[pygame.K_LEFT]:
        direc = 'W'
        # ev_mger.post(pyv.EngineEvTypes.Keydown, key='left')
        # print('pleft')
    elif active_keys[pygame.K_RIGHT]:
        direc = 'E'
        # ev_mger.post(pyv.EngineEvTypes.Keydown, key='right')
        # print('pright')
    elif active_keys[pygame.K_UP]:
        direc = 'N'
    elif active_keys[pygame.K_DOWN]:
        direc = 'S'

    # - logic
    if glvars.prev_time_info:
        dt = (time_info - glvars.prev_time_info)
    else:
        dt = 0
    glvars.prev_time_info = time_info
    ev_mger.post(pyv.EngineEvTypes.Update)
    ev_mger.update()

    # deplacement sales poussés vers le server
    # print(net_eng.mdata_peek().content)
    # TODO fin if this is
    # possible ??
    # net_eng.mdata_peek().content['x'] += 10.0
    # In the meantime, we work only with MESSAGING. Like this:
    # bmsg = [0,]
    # bmsg.extend(map(ord,list('truc')))
    if direc:
        if (cached_dir is not None) and cached_dir == direc:
            mimic_packet = cached_packet
        else:
            mimic_packet = gen_packet_for_direction(direc)
            cached_dir, cached_packet = direc, mimic_packet
        net_eng.push_data(mimic_packet)

    # puisqu'on sait pas encore faire de lien propre entre mutableData & la donnée qui est lue par le jeu courant,
    # je fais <JUSTE> cette copie sauvage, ici:
    if net_eng.is_data_available():
        ref_state.players[0]['x'] = int(
            net_eng.mdata_peek().content['x']
        )
        ref_state.players[0]['y'] = int(
            net_eng.mdata_peek().content['y']
        )

    # pyv.systems_proc(dt)
    scr = pyv.get_surface()
    scr.fill(glvars.BG_COLOR)
    pygame.draw.rect(
        scr, 'blue', (ref_state.players[0]['x'], ref_state.players[0]['y'], 24, 24)
    )
    pyv.flip()
    pyv.vars.clock.tick(60)


@pyv.declare_end
def done(vmst=None):
    net_eng.graceful_exit()  # close colyseus properly
    pyv.close_game()
    print('fin de jeu')
