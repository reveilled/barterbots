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

	def parse_offer(self, bytestream):
		header = bytestream[:7]
		item_list = bytestream[7:]
		user_id, item_id, num_items = struct.unpack('>LHB', header)
		offered_items = {}
		for index in range(num_items):
			start, end = 3*index, (3*index + 3)
			offer_item, offer_quantity = struct.unpack('>HB',item_list[start:end])
			offered_items[offer_item] = offer_quantity

		self.user_id = user_id
		self.target_item_id = item_id
		self.offered_items = offered_items

	def parse_vote(self, bytestream):
		pass

	def parse_join(self, bytestream):
		pass

	def pack_offer(self, action_type, user, target_item, item_list):
		item_stream = b''.join([struct.pack('>HB', i, item_list[i]) for i in item_list])
		header_stream = struct.pack('>BLHB', action_type.value, user, target_item, len(item_list))
		return header_stream + item_stream

	def pack_vote(self, vote_type, user, item):
		pass

	def pack_join(self, join_type, bot_id, channel_name):
		pass
