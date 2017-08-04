# barterbots
This program is meant to allow users to barter with individual bots. A player starts by connecting to the broker, arranging access to individual bots, and putting requests to vote.

Each piece of information is tagged with a value and a required number of votes (X yes, (X yes, Y No), Y No, etc). Bots have access to the values of each item for negotiating purposes.

Trade and Vote Actions 
An action consists of the type (1-byte), user id (4-byte), an item id (2-byte), the data for the specific type, then a crc32 or cyptographic signature. Any data past the crc/signature is discarded. a number of items, then a list of the offered items in the form of (item (2-byte), quantity(1-byte)) and a crc32 or signature depending on how protected you want it to be.

Action types:
1. Initial Offer - The data consists of a 1-byte number of item offers. The list is packed in the form of (item id 1 (2-byte), quantity 1 (1-byte, signed)),... (item id n (2-byte), quantity n (1-byte, signed)). A length of zero is considered an inquiry for an acceptable offer.
2. Rejection/Counter - The data consists of a 1-byte number of item offers. This list is packed as with the initial offer but only consists of items to be added/removed from the current state of the trade.
3. Accept -  The data consists of the timestamp of the offer's expiration (32-bit timestamp).
4. Vote - No further data is required
5. Vote response - 1-byte yes/no value followed by the an item list that was agreed upon


Bots
A bot maintains a value vector for every item in the system.
A bot must always be a bit greedy and ask for more than it actually wants.
A bot determines the value of a trade by takeing a dot product of the item quantities.
The value of a vote is determined by multiplying the value of the item a scaling factor (generosity/greed/frustration)
If the value of the trade is greater than the value of the vote the bot issues an acceptance.
If the value of the trade is less than the value of the vote the bot issues a rejection/counter.
Upon confirmation of an accepted trade the bot stores the agreed vote response until the trade timeout occurs.
When a vote is requested the bot checks for any accepted trades. If they are not expired the bot casts the vote with a list of agreed items.
When a vote is requested and no accepted trades exist a random yes/no is chosen. This probability must diminish with the item value. A bot may not attach an item list on a random vote.


Broker
A broker handles initial connections for the player.
The broker maintains a channel to each bot with mqtt.
The broker provides temporary mqtt channels for players to connect to to negotiate with bots when a player requests to speak to a bot
The broker initiates a vote for a player to have access to a specific item.
If a bot submits a list of items with a vote it is automatically trans

	Commands
		1. Connect to - tell a bot to connect to a given channel
		2. Disconnect from - tell a bot to disconnect from a given channel
		3. Vote - provide a vote for a player to access an item

