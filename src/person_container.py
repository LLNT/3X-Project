from typing import Dict,List,Tuple
from . import person
class Main:
    def __init__(self):
        self.name="" #type:str
        self.people=[] #type:List[person.Person]
        self.controller={} #type:Dict[str,int]
        self.position={} #type:Dict[str,Tuple[int,int]]
        self.movable={} #type:Dict[str,bool]
        self.army={} #type:Dict[str,str]
        self.AItype={} #type:Dict[str,Tuple[int,str]]
    def __init__(self,armylist,personbank,ai_config):
        self.name=armylist["Name"]
        self.people=[]
        self.controller={}
        self.position={}
        self.movable={}
        self.army={}
        self.AItype={}
        for item in armylist["Armies"]:
            for p in item["Member"]:
                self.people.append(personbank[p["Id"]])
                self.controller[p["Id"]]=item["Controller"]
                self.position[p["Id"]]=(p["X"],p["Y"])
                self.movable[p["Id"]]=True
                self.army[p["Id"]]=item["Name"]
                self.AItype[p["Id"]]=(p["PRI"],ai_config[p["AI"]])
