from enum import Enum
import struct

class Action(Enum):
    NONE = 0
    OFFER_INITIAL = 1
    OFFER_COUNTER = 2
    OFFER_REJECT = 3
    OFFER_ACCEPT = 4
    VOTE_REQUEST = 5
    VOTE_RESPONSE = 6
    JOIN_COMMAND = 7
    JOIN_ACKNOWLEDGE = 8

class Vote(Enum):
    NO = 0
    YES = 1

class bartermessage(object):
    def __init__(self):
        self.action = Action.NONE

    def parse(self, bytestream):
        #determine the type
        #Auto single byte to int feels weird
        self.action = Action(bytestream[0])
        if self.action in [Action.OFFER_INITIAL, Action.OFFER_COUNTER, Action.OFFER_REJECT, Action.OFFER_ACCEPT] :
            self.parse_offer(bytestream[1:])
        elif self.action in [Action.VOTE_REQUEST, Action.VOTE_RESPONSE]:
            self.parse_vote(bytestream[1:])
        elif self.action in [Action.JOIN_COMMAND, Action.JOIN_ACKNOWLEDGE]:
            self.parse_join(bytestream[1:])
        else:
            #raise a type error
            pass

    def parse_item_list(self, bytestream):
        num_items = bytestream[0]
        item_list = bytestream[1:]
        offered_items = {}
        for index in range(num_items):
            start, end = 3*index, (3*index + 3)
            offer_item, offer_quantity = struct.unpack('>HB',item_list[start:end])
            offered_items[offer_item] = offer_quantity

        self.item_list = offered_items    

    def pack_item_list(self, item_list_dict):
        flattened_list = [struct.pack('>HB', i, item_list_dict[i]) for i in item_list_dict]
        stream = struct.pack('>B',len(item_list_dict)) + b''.join(flattened_list)
        return stream

    def parse_offer(self, bytestream):
        header = bytestream[:6]
        item_stream = bytestream[6:]

        self.user_id, self.item_id = struct.unpack('>LH', header)
        self.parse_item_list(item_stream)

    def parse_vote(self, bytestream):
        self.user_id, self.item_id = struct.unpack('>LH',bytestream[:6])
        if self.action == Action.VOTE_RESPONSE:
            self.vote = bytestream[6]
            self.parse_item_list(bytestream[7:])

    def parse_join(self, bytestream):
        self.bot_name, self.channel = bytestream.split(b':')

    def pack_offer(self, action_type, user, target_item, item_list):
        item_stream = self.pack_item_list(item_list)
        header_stream = struct.pack('>BLH', action_type.value, user, target_item)
        return header_stream + item_stream

    def pack_vote(self, vote_type, user, item, response = Vote.NO, item_list=None):
        header_stream = struct.pack('>BLH', vote_type.value, user, item)
        if vote_type == Action.VOTE_REQUEST:
            return header_stream
        elif item_list is None:
            item_list = {}
        
        item_stream = self.pack_item_list(item_list)
        return header_stream + struct.pack('>B', response.value) + item_stream 

    def pack_join(self, join_type, bot_id, channel_name):
        return struct.pack('>B', join_type.value) + bot_id + b':' + channel_name
