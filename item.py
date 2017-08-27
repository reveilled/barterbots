from enum import Enum
from collections import defaultdict

class PossessorType(Enum):
    BOT = 0
    USER = 1
    ETHER = 2

class TransferOutcome(Enum):
    SUCCESS = 0
    UNKNOWN_FAILURE = 1
    SOURCE_DOES_NOT_EXIST = 2
    DEST_DOES_NOT_EXIST = 3
    SOURCE_INSUFFICIENT_QUANTITY = 4


class ItemDetails(object):
    def __init__(self, item_id, name, description, data):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.data = data

class ItemManager(object):
    def __init__(self):
        self.inventories = defaultdict(dict)
        self.item_details = defaultdict(None)

    def add_item_to_inventory(self, dest_id, item_id, item_qty_delta):
        #get the target's inventory
        inventory = self.inventories[dest_id]
        item_qty = inventory.get(item_id, 0)
        item_qty += item_qty_delta
        inventory[item_id] = item_qty

        return TransferOutcome.SUCCESS

    def remove_item_from_inventory(self, src_id, item_id, item_qty_delta):
        inventory = self.inventories[src_id]
        item_qty = inventory.get(item_id, 0)
        if item_qty < item_qty_delta:
            return TransferOutcome.SOURCE_INSUFFICIENT_QUANTITY
        item_qty -= item_qty_delta
        inventory[item_id] = item_qty

        return TransferOutcome.SUCCESS

    #return an outcome code after doing transfer
    def transfer_item(self, src_id, dest_id, item_id, item_qty):

        #Take the item out of the source's inventory
        remove_outcome = remove_item_from_inventory(src_id, dest_id, item_id, item_qty)

        if remove_outcome != TransferOutcome.SUCCESS:
            return remove_outcome
                
        #then put it in the new inventory
        add_outcome = add_item_to_inventory(dest_id, item_id, item_qty)

        return add_outcome

    def add_item_details(self, item_id, name, description, data):
        self.item_details[item_id] = ItemDetails(item_id, name, description, data)
        
    def get_item_name(self, item_id):
        details = self.item_details[item_id]
        if details is None:
            return None
        return details.name

    def get_item_description(self, item_id):
        details = self.item_details[item_id]
        if details is None:
            return None
        return details.description

    def get_item_data(self, item_id):
        details = self.item_details[item_id]
        if details is None:
            return None
        return details.data
