from typing import Dict,List
class Itemtype:
    def __init__(self):
        self.name=""          #type:str
        self.max_use=0        #type:int
        self.weapontype=""    #type:str
        self.power=0          #type:int
        self.weight=0         #type:int
        self.hit=0            #type:int
        self.critical=0       #type:int
        self.max_range=0      #type:int
        self.min_range=0      #type:int
        self.ability_bonus={} #type:Dict[str,int]
        self.special_effect=[]#type:List[str]
        self.rank=0           #type:int
        self.skills=[]        #type:List[str]
        self.value=0          #type:int
        self.character_only=[]  # type:List[str]
        self.use_effect=""  # type:str
        self.wand={}            #{"Type":int,"Effect":str}
        self.status=[]          #[{"Status":str,"Rest":int,"Chance":int},]
    def __init__(self,name,use,weap,pw,wt,ht,ct,max_r,min_r,bonus,special,rk,sk,val,charonly,use_eff,wand,status):
        self.name=name
        self.max_use=use
        self.weapontype=weap
        self.power=pw
        self.weight=wt
        self.hit=ht
        self.critical=ct
        self.max_range=max_r
        self.min_range=min_r
        self.ability_bonus=bonus
        self.special_effect=special
        self.rank=rk
        self.skills=sk
        self.value=val
        self.character_only=charonly
        self.use_effect=use_eff
        self.wand=wand
        self.status=status
class ItemtypeBank:
    def __init__(self):
        self.itemtypebank={} #type:Dict[str,Itemtype]
    def __init__(self,itemtypelist):
        self.itemtypebank={}
        for item in itemtypelist:
            itemtype=Itemtype(item["Name"],item["Max_use"],item["Weapon_type"],
                              item["Power"],item["Weight"],item["Hit"],
                              item["Critical"],item["Max_range"],item["Min_range"],
                              item["Ability_bonus"],item["Special_effect"],item["Rank"],
                              item["Skills"],item["Value"],item["Character_only"],item["Use"],item["Wand"],item["Status"])
            self.itemtypebank[item["Name"]]=itemtype

class Main:
    def __init__(self):
        self.itemtype_bank={} #type:Dict[str,Itemtype]
    def __init__(self,data):
        self.itemtype_bank=ItemtypeBank(data.item_type_list).itemtypebank
