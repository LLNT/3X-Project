from . import item
import random
from typing import List,Dict,Tuple
from .utility import *
class Person:
    def __init__(self):
        self.pid = ""        #type:str
        self.name = ""       #type:str
        self.cls = ""        #type:str
        self.pic = ""        #type:str
        self.icon = ""       #type:str
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
        self.status={}       #type:Dict[str,int]
        self.coefficient=0.0 #type:float
        self.bonus=0         #type:int
        self.battlecard={}
    def __init__(self,pid,name,cls,ability,skills,pic,icon,weapon_rank_bonus,items,support,cls_weapon_rank,color,attr,growth,
                 cls_abl_limit,coe,bon,battlecard):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.growth=growth
        self.skills=skills
        self.pic=pic
        self.icon=icon
        self.weapon_rank=cls_weapon_rank[self.cls].copy()
        self.ability_limit=cls_abl_limit[self.cls].copy()
        self.suprank={}
        self.supdata={}
        self.color=color
        self.attribute=attr
        self.equiped=0
        self.status={}
        self.coefficient=coe
        self.bonus=bon
        if len(support)>0:
            for obj in support:
                self.suprank[obj]=0
                self.supdata[obj]=[support[obj]["Base"],support[obj]["Growth"]]
                '''if self.supdata[obj][0]>50:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>100:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>200:
                    self.suprank[obj]+=1'''
        for wp in weapon_rank_bonus:
            self.weapon_rank[wp]+=weapon_rank_bonus[wp]
        self.item=items
        self.battlecard=battlecard

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
        self.ability["LV"]+=1
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

    def use_item(self,_item):
        i=_item #type:item.Item
        if len(i.itemtype.character_only)>0:
            if not self.pid in i.itemtype.character_only:
                return 2
        r=i.use_item(self)
        i.use-=1
        if i in self.item:
            if i.use==0:
                self.banish(i)
        return r

    def add_status(self,sta,rest):
        if not (sta in self.status):
            self.status[sta]=rest
            return
        r0=self.status[sta]
        if rest>r0:
            self.status[sta]=rest
        if sta=="Power":
            self.ability["MGC"]-=r0
        if sta=="Restore":
            self.ability["DEF"]-=r0
        if sta=="Barrier":
            self.ability["RES"]-=r0
        return

    def can_promote(self,global_vars):
        if not (self.cls in global_vars.cls_rank["Low"]):
            return []
        if not self.ability["LV"]>=10:
            return []
        if self.cls=="Archer":
            return ["Sniper"]
        if self.cls=="Cavalier":
            return ["Paladin"]
        return []

    def promote(self,cl,g_vars):
        c_tar=g_vars.clsBank[cl]
        for wptype in c_tar.weapon_rank:
            self.weapon_rank[wptype]+=c_tar.weapon_rank[wptype]
            if self.weapon_rank[wptype]>400:
                self.weapon_rank[wptype]=400
        self.ability_limit=c_tar.ability_limit.copy()
        promote_base=g_vars.data.cls_promote_bonus[self.cls]
        promote_tar=g_vars.data.cls_promote_bonus[cl]
        abl_ori=self.ability.copy()
        promote_bonus={}
        for abl in promote_tar:
            promote=promote_tar[abl]-promote_base[abl]
            if promote+self.ability[abl]>=self.ability_limit[abl]:
                promote=self.ability_limit[abl]-self.ability[abl]
            promote_bonus[abl]=promote
            self.ability[abl]+=promote
        self.cls=cl
        self.ability["LV"]=1
        self.ability["EXP"]=0
        return promote_bonus,abl_ori


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
                          persondict[pid]["Skills"],persondict[pid]["Picture"],persondict[pid]["Icon"],persondict[pid]["Weapon Rank Bonus"],
                          items,persondict[pid]["Support"],cls_weapon_rank,persondict[pid]["Color"],
                          persondict[pid]["Attribute"],persondict[pid]["Growth"],cls_abl_lmt,
                          persondict[pid]["Coefficient"],persondict[pid]["Bonus"],persondict[pid]["Battlecard"])
            self.person_bank[pid]=person


class Main:
    def __init__(self):
        self.person_bank={}  #type:Dict[str,Person]
    def __init__(self,data,itembank):
        self.person_bank=PersonBank(data.pidlist,data.persondata,itembank,data.cls_weapon_rank,data.cls_ability_limit).person_bank
