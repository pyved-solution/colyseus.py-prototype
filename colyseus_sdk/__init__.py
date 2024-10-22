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
