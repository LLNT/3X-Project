from typing import List
from . import terrain
class Main:
    def __init__(self):
        self.name="" #type:string
        self.M=0   #type:int
        self.N=0   #type:int
        self.map=[[]] #type:List[List[terrain.Terrain]
    def __init__(self,terrain_map,terrain_bank):
        self.name=terrain_map["Name"]
        self.M=terrain_map["M"]
        self.N=terrain_map["N"]
        self.map=[]
        for i in range(self.M):
            row=[]
            for j in range(self.N):
                row.append(terrain_bank[terrain_map["Map"][i][j]])
            self.map.append(row)
            del(row)

