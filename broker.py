#! /usr/bin/python3
from barterprot import bartermessage, Vote, Action
import random
import argparse
import paho.mqtt.client as mqtt

class Broker(object):
    def __init__(self, mqtt_server = None):
        #init props
        self.player_channels = []
        self.bot_channels = []

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

    def join_bot_channel(self, topic):
        self.client.subscribe(topic)
        self.bot_channels.append(topic)

    def join_player_channel(self, topic):
        self.client.subscribe(topic)
        self.player_channels.append(topic)

    def connect_callback(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        #bot default channel
        self.join_bot_channel('broker/room')
        #player default channel
        self.join_player_channel('broker/lobby')
        
    def message_callback(self, client, userdata, msg):
        #handle it
        topic = msg.topic

        #bots
        if topic in self.bot_channels:
            message = bartermessage()
            message.parse(msg.payload)
            print('Bot', self.bot_id, 'received message for', topic, ':', message.action)
            self.action_handlers[message.action](message)

        #humans
        elif topic in self.player_channels:
            message = str(msg.payload,'UTF8')
            self.human_message_handle(message, msg.topic)

        #Make the sender know we are very confused as to who they are
        else:
            self.client.publish(topic, 'ERROR: message received in unmapped channel')

    def join(self, server, port, thing):
        self.client.connect(server, port, thing)

    def loop(self):
        self.client.loop_forever()

    def default_message_handle(self, message):
        print('Currently not handling messages of type',message.action)

    def tmpchannel(self):
        #TODO: Random unique channel names
        #stub this to AAAA for now
        return 'AAAA'

    #The broker mainly handles arranging private rooms for bots and facilities vote-based access to items
    #The first thing user should do is send a join command for the broker and join that channel
    #Rinse and repeat a couple of times to get a private channel going
    #  1. "join" command requires a user id and target bot. A channel may be optionally specified.
    #     If no channel is specified, a random one is generated for the acknowledgement
    #     The acknowledgment consists of ACK in front of the join command including the named or generated channel
    #     A rejection consists of REJ in front of the command followed by a plain text reason
    #       EX1: User 1 wants to talk to the broker over the topic "AAAA" the would send "JOIN 1 BROKER AAAA"
    #            Broker posts "ACK JOIN 1 BROKER AAAA"
    #       EX2: User 13 wants to talk to "wonderbot" over a random topic and sends "JOIN 13 WONDERBOT"
    #            Broker posts "ACK JOIN 13 WONDERBOT BBBB"
    #       EX3: User 1 wants to talk to wonderbot on the same topic channel generated in the previous example
    #            User 1 sends "JOIN 1 WONDERBOT BBBB"
    #            Broker publishes "REJ JOIN 1 WONDERBOT BBBB TOPIC IN USE"
    #  2. "vote" command requries a user id and an item ID.
    #     It them polls bots in the private channels, counts the votes, then returns the result and any associated data.
    #       Ex. User 1 wants access to item 13 it would send "VOTE 1 13"
    #           The broker would return "RESULT 1 13 DENIED" if there were insufficient votes
    #           The broker would return "RESULT 1 13 VICTORYDATA" if there were sufficient votes
    #           where VICTORYDATA is the data associated with item 13

    def human_message_handle(self, message, topic):
        try:
            message_parts = message.split(' ')

            command = message_parts[0].upper()
            #handle our responses delicately
            if command in ['ACK', 'REJ', 'RESULT']:
                return

            user_id = int(message_parts[1])

            if command == 'JOIN':
                target_bot = message_parts[2]
                if len(message_parts) >= 4:
                    channel = message_parts[3]
                else:
                    channel = self.tmpchannel()
                self.do_join(user_id, target_bot, channel, topic)

            elif command == 'VOTE':
                item_id = int(message_parts[2])
                self.vote_poll(user_id, item_id, topic)

        except:
            print('Error handling human message in topic {}: {}'.format(topic,message))

    def vote_poll(self, user, item, topic):
        #TODO: Poll subscribed bots
        #TODO: Manage access to items
        result = "DENIED"
        #return denied for now
        self.client.publish(topic, 'RESULT {user_id} {item_id} {value}\n'.format(user_id=user, item_id = item, value=result))    

    def do_join(self, user, bot, dest_topic, src_topic):
        if bot == 'BROKER':
            self.join_player_channel(dest_topic)
            self.client.publish(src_topic, 'ACK JOIN {user_id} {bot_id} {topic}\n'.format(user_id=user, bot_id=bot, topic=dest_topic))
        else:
            #TODO: Handle bots we have control over
            self.client.publish(src_topic, 'REJ JOIN {user_id} {bot_id} {topic} BOT NOT PRESENT\n'.format(user_id=user, bot_id=bot, topic=dest_topic))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Barter broker using mqtt')
    parser.add_argument('server', help='The mqtt server to connnect to')
    args = parser.parse_args()

    broker = Broker(args.server)
    broker.loop()
