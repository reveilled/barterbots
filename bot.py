#! /usr/bin/python3
import struct
from barterprot import bartermessage, Vote, Action
import random
import argparse
import paho.mqtt.client as mqtt

class Bot(object):
	def __init__(self, bot_id, mqtt_server = None):
		#init props
		self.bot_id = bot_id
		self.accepted_trades = []

		#register handlers
		self.action_handlers = { Action.OFFER_INITIAL : self.default_message_handle,
							Action.OFFER_COUNTER : self.default_message_handle,
							Action.OFFER_REJECT : self.default_message_handle,
							Action.OFFER_ACCEPT : self.default_message_handle,
							Action.VOTE_REQUEST : self.default_message_handle,
							Action.VOTE_RESPONSE : self.default_message_handle,
							Action.JOIN_COMMAND : self.default_message_handle,
							Action.JOIN_ACKNOWLEDGE : self.default_message_handle
						}
		self.client = mqtt.Client()
		self.client.on_connect = self.connect_callback
		self.client.on_message = self.message_callback


		if mqtt_server:
			#join mqtt_server
			self.join(mqtt_server, 1883, 60)

	def connect_callback(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))
		self.client.subscribe('broker/room')
	
	def message_callback(self, client, userdata, msg):
		message = bartermessage()
		message.parse(msg.payload)
		print('Bot', self.bot_id, 'received message for', msg.topic, ':', message.action)
		#handle it
		self.action_handlers[message.action](message)

		#message = msg.payload
		#print('Bot', self.bot_id, 'received message for ', msg.topic, ':', message)

	def join(self, server, port, thing):
		self.client.connect(server, port, thing)

	def loop(self):
		self.client.loop_forever()

	def default_message_handle(self, message):
		print('Currently not handling messages of type',message.action)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Barter bot using mqtt')
    parser.add_argument('name', help='A name for this bot to identify itself')
    parser.add_argument('server', help='The mqtt server to connnect to')
    args = parser.parse_args()

    mybot = Bot(args.name, args.server)
    mybot.loop()
