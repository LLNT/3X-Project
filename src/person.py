import item
from typing import List,Dict,Tuple
class Person:
    def __init__(self):
        self.pid = ""        #type:str
        self.name = ""       #type:str
        self.cls = ""        #type:str
        self.pic = ""        #type:str
        self.ability = []    #type:List[Dict[str,int]]
        self.skills = []     #type:List[str]
        self.weapon_rank={}  #type:Dict[str,int]
        self.item=[]         #type:List[item.Item]
        self.suprank={}      #type:Dict[str,int]
        self.supdata={}      #type:Dict[str,Tuple[int,int]]
        self.attribute=""    #type:str
        self.color=""        #type:str
    def __init__(self,pid,name,cls,ability,skills,pic,weapon_rank_bonus,items,support,cls_weapon_rank,color,attr):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.skills=skills
        self.pic=pic
        self.weapon_rank=cls_weapon_rank[self.cls].copy()
        self.suprank={}
        self.supdata={}
        self.color=color
        self.attribute=attr
        if len(support)>0:
            for obj in support:
                self.suprank[obj]=0
                self.supdata[obj]=(support[obj]["Base"],support[obj]["Growth"])
                if self.supdata[obj][0]>50:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>100:
                    self.suprank[obj]+=1
                if self.supdata[obj][0]>200:
                    self.suprank[obj]+=1
        for wp in weapon_rank_bonus:
            self.weapon_rank[wp]+=weapon_rank_bonus[wp]
        self.item=items

class PersonBank:
    def __init__(self):
        self.personbank={}   #type:Dict[str,Person]
    def __init__(self,idlist,persondict,itembank,cls_weapon_rank):
        self.person_bank={}
        for pid in idlist:
            items=[]
            for item in persondict[pid]["Init_item"]:
                items.append(itembank[item])
            person=Person(pid,persondict[pid]["Name"],persondict[pid]["Cls"],persondict[pid]["Ability"],
                          persondict[pid]["Skills"],persondict[pid]["Picture"],persondict[pid]["Weapon Rank Bonus"],
                          items,persondict[pid]["Support"],cls_weapon_rank,persondict[pid]["Color"],persondict[pid]["Attribute"])
            self.person_bank[pid]=person


class Main:
    def __init__(self):
        self.person_bank={}  #type:Dict[str,Person]
    def __init__(self,data,itembank):
        self.person_bank=PersonBank(data.pidlist,data.persondata,itembank,data.cls_weapon_rank).person_bank