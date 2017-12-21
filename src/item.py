from typing import Dict
import itemtype
class Item:
    def __init__(self):
        self.itemid=None      #type:int
        #id to locate the item
        self.itemtype=None    #type:itemtype.Itemtype
        self.use=0             #type:int

    def __init__(self,iid,itemtype,use):
        self.itemid=iid
        self.itemtype=itemtype
        self.use=use

class ItemBank:
    def __init__(self):
        self.itembank={}   #type:Dict[int,Item]
    def __init__(self,init_item_list,itemtype_bank):
        self.itembank={}
        for item in init_item_list:
            new_item=Item(item["Id"],itemtype_bank[item["Itemtype"]],item["Use"])
            self.itembank[item["Id"]]=new_item


class Main:
    def __init__(self):
        self.item_bank={}  #type:Dict[int,Item]
    def __init__(self,data,item_type_bank):
        self.item_bank=ItemBank(data.init_item_list,item_type_bank).itembank