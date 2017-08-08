import struct
import barterprot
import random

class Bot(object):
    def __init__(self, bot_id, mqtt_server = None):
        self.bot_id = bot_id
        self.accepted_trades = []
        if mqtt_server:
            pass
            #join mqtt_server

