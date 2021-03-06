from typing import Dict,List


class Terrain:
    def __init__(self):
        self.typename=""   #type:str
        self.enhance={}    #type:Dict[str,Dict[str,Dict[str,int]]]
        self.decay={}      #type:Dict[str,Dict[str,int]]
    def __init__(self,typename,enhance,decay):
        self.typename=typename
        self.enhance=enhance#battle_enhance[self.typename]
        self.decay=decay#move_decay[self.typename]

class TerrainBank:
    def __init__(self):
        self.terrain_bank={} #type:Dict[str,Terrain]
    def __init__(self,typenamelist,enhance,decay):
        self.terrain_bank={}
        for typename in typenamelist:
            terrain=Terrain(typename,enhance[typename],decay[typename])
            self.terrain_bank[typename]=terrain

class Main:
    def __init__(self):
        self.terrain_bank={} #type:Dict[str,Terrain]
    def __init__(self,data):
        self.terrain_bank=TerrainBank(data.terrain_typenames,data.terrain_battle_enhance,data.move_decay).terrain_bank

