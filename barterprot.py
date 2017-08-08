from enum import Enum
import struct

class Action(enum):
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

	def parse(bytestream):
		#determine the type
		self.action = Action(struct.parse('B',bytestream[0])

	def parse_offer(bytestream):
		pass

	def parse_vote(bytestream):
		pass

	def parse_join(bytestream):
		pass

	def pack_offer(action_type, user, target_item, item_list):
		pass

	def pack_vote(vote_type, user, item):
		pass

	def pack_join(join_type, bot_id, channel_name):
		pass
