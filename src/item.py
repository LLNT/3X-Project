from typing import Dict
import itemtype
import person
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

    def use_item(self,_p):
        p=_p   #type:person.Person
        use_eff=self.itemtype.use_effect.split(" ")
        t=0
        while t<len(use_eff):
            if use_eff[t]=="UNAVAILABLE":
                break
            if use_eff[t]=="HEAL":
                p.ability["HP"]+=int(use_eff[t+1])
                if p.ability["HP"]>p.ability["MHP"]:
                    p.ability["HP"]=p.ability["MHP"]
                t+=2
                continue
            if use_eff[t] in p.ability:
                p.ability[use_eff[t]]+=int(use_eff[t+1])
                if p.ability[use_eff[t]]>p.ability_limit[use_eff[t]]:
                    p.ability[use_eff[t]]=p.ability_limit[use_eff[t]]
                t+=2
                continue
            if use_eff[t]=="PROMOTE":
                t+=1
                continue
            if use_eff[t]=="BARRIER":
                t+=1
                p.ability["RES"] += 7
                p.add_status("Barrier", 7)
        return use_eff

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