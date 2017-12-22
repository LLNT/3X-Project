import item
from typing import List,Dict
class Person:
    def __init__(self):
        self.pid = ""        #type:str
        self.name = ""       #type:str
        self.cls = ""        #type:str
        self.ability = []    #type:List[Dict[str,int]]
        self.skills = []     #type:List[str]
        self.item=[]         #type:List[item.Item]
    def __init__(self,pid,name,cls,ability,skills,items):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.skills=skills
        self.item=items



class PersonBank:
    def __init__(self):
        self.personbank={}   #type:Dict[str,Person]
    def __init__(self,idlist,persondict,itembank):
        self.person_bank={}
        for pid in idlist:
            items=[]
            for item in persondict[pid]["Init_item"]:
                items.append(itembank[item])
            person=Person(pid,persondict[pid]["Name"],persondict[pid]["Cls"],persondict[pid]["Ability"],
                          persondict[pid]["Skills"],items)
            self.person_bank[pid]=person


class Main:
    def __init__(self):
        self.person_bank={}  #type:Dict[str,Person]
    def __init__(self,data,itembank):
        self.person_bank=PersonBank(data.pidlist,data.persondata,itembank).person_bank