import item
import random
from typing import List,Dict,Tuple
from utility import *
class Person:
    def __init__(self):
        self.pid = ""        #type:str
        self.name = ""       #type:str
        self.cls = ""        #type:str
        self.pic = ""        #type:str
        self.ability ={}     #type:Dict[str,int]
        self.skills = []     #type:List[str]
        self.ability_limit={}#type:Dict[str,int]
        self.weapon_rank={}  #type:Dict[str,int]
        self.item=[]         #type:List[item.Item]
        self.suprank={}      #type:Dict[str,int]
        self.supdata={}      #type:Dict[str,Tuple[int,int]]
        self.attribute=""    #type:str
        self.color=""        #type:str
        self.equiped=0       #type:int
        self.growth={}       #type:Dict[str,int]
    def __init__(self,pid,name,cls,ability,skills,pic,weapon_rank_bonus,items,support,cls_weapon_rank,color,attr,growth,cls_abl_limit):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.growth=growth
        self.skills=skills
        self.pic=pic
        self.weapon_rank=cls_weapon_rank[self.cls].copy()
        self.ability_limit=cls_abl_limit[self.cls].copy()
        self.suprank={}
        self.supdata={}
        self.color=color
        self.attribute=attr
        self.equiped=0
        if len(support)>0:
            for obj in support:
                self.suprank[obj]=0
                self.supdata[obj]=(support[obj]["Base"],support[obj]["Growth"])
                '''if self.supdata[obj][0]>50:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>100:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>200:
                    self.suprank[obj]+=1'''
        for wp in weapon_rank_bonus:
            self.weapon_rank[wp]+=weapon_rank_bonus[wp]
        self.item=items

    def get_equip(self):
        if len(self.item)<1:
            return None
        for weap in self.item:
            if is_weapon(weap.itemtype.weapontype):
                if weap.itemtype.rank<=self.weapon_rank[weap.itemtype.weapontype]:
                    if self.equiped==0:
                        self.equip(weap)
                    return weap
        return None

    def equip(self,_item):
        if self.equiped==1:
            eqp=self.get_equip()
            self.dequip(eqp)
        equip_item=_item
        if equip_item not in self.item:
            self.item.append(equip_item)
        p=self.item.index(equip_item)
        self.item[p]=self.item[0]
        self.item[0]=equip_item
        for abl in self.ability:
            self.ability[abl]+=equip_item.itemtype.ability_bonus[abl]
        self.equiped=1
        return

    def dequip(self,_item):
        dequip_item=_item   #type:item.Item
        for abl in self.ability:
            self.ability[abl]-=dequip_item.itemtype.ability_bonus[abl]
        if self.ability["HP"]>self.ability["MHP"]:
            self.ability["HP"]=self.ability["MHP"]
        self.equiped=0
        return

    def banish(self,_item):
        if self.get_equip()==_item:
            self.dequip(_item)
        self.item.remove(_item)
        del(_item)
        return

    def lv_up(self):
        growth_rec={}
        for abl in self.growth:
            if self.growth[abl]>0:
                base=int(self.growth[abl]/100)
                p=self.growth[abl]-100*base
                q=random.randint(0,99)
                if q<p:
                    base+=1
                wpbonus=0
                if self.equiped==1:
                    wpbonus=self.get_equip().itemtype.ability_bonus[abl]
                if self.ability[abl]+base>self.ability_limit[abl]+wpbonus:
                    base=self.ability_limit[abl]+wpbonus-self.ability[abl]
                growth_rec[abl]=base
                self.ability[abl]+=base
            elif self.growth[abl]<0:
                gr=-self.growth[abl]
                base=int(gr/100)
                p=gr-100*base
                q=random.randint(0,99)
                if q<p:
                    base+=1
                wpbonus=0
                if self.equiped==1:
                    wpbonus=self.get_equip().itemtype.ability_bonus[abl]
                if self.ability[abl]-base<wpbonus:
                    base=self.ability[abl]-wpbonus
                growth_rec[abl]=-base
                self.ability[abl]-=base
            else:
                growth_rec[abl]=0
        return growth_rec


class PersonBank:
    def __init__(self):
        self.personbank={}   #type:Dict[str,Person]
    def __init__(self,idlist,persondict,itembank,cls_weapon_rank,cls_abl_lmt):
        self.person_bank={}
        for pid in idlist:
            items=[]
            for item in persondict[pid]["Init_item"]:
                items.append(itembank[item])
            person=Person(pid,persondict[pid]["Name"],persondict[pid]["Cls"],persondict[pid]["Ability"],
                          persondict[pid]["Skills"],persondict[pid]["Picture"],persondict[pid]["Weapon Rank Bonus"],
                          items,persondict[pid]["Support"],cls_weapon_rank,persondict[pid]["Color"],
                          persondict[pid]["Attribute"],persondict[pid]["Growth"],cls_abl_lmt)
            self.person_bank[pid]=person


class Main:
    def __init__(self):
        self.person_bank={}  #type:Dict[str,Person]
    def __init__(self,data,itembank):
        self.person_bank=PersonBank(data.pidlist,data.persondata,itembank,data.cls_weapon_rank,data.cls_ability_limit).person_bank