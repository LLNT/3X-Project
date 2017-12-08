from typing import List,Dict
class Person:
    def __init__(self):
        self.pid = ""        #type:str
        self.name = ""       #type:str
        self.cls = ""        #type:str
        self.ability = []    #type:List[Dict[str,int]]
        self.skills = []     #type:List[str]
        pass
    def __init__(self,pid,name,cls,ability,skills):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.skills=skills


class PersonBank:
    def __init__(self):
        self.personbank={}   #type:Dict[str,Person]
    def __init__(self,idlist,persondict):
        self.person_bank={}
        for pid in idlist:
            person=Person(pid,persondict[pid]["Name"],persondict[pid]["Cls"],persondict[pid]["Ability"],
                          persondict[pid]["Skills"])
            self.person_bank[pid]=person


class Main:
    def __init__(self):
        self.person_bank={}  #type:Dict[str,Person]
    def __init__(self,data):
        self.person_bank=PersonBank(data.pidlist,data.persondata).person_bank