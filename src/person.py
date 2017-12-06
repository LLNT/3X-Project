
class Person:
    def __init__(self):
        pass
    def __init__(self,pid,name,cls,ability,skills):
        self.pid=pid
        self.name=name
        self.cls=cls
        self.ability=ability
        self.skills=skills

class PersonBank:
    def __init__(self):
        pass
    def __init__(self,idlist,persondict):
        self.person_bank={}
        for pid in idlist:
            person=Person(pid,persondict[pid]["Name"],persondict[pid]["Cls"],persondict[pid]["Ability"],
                          persondict[pid]["Skills"])
            self.person_bank[pid]=person

class Main:
    def __init__(self):
        pass
    def __init__(self,data):
        self.person_bank=PersonBank(data.pidlist,data.persondata).person_bank