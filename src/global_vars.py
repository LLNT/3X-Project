from terrain import Main as Terrain
from cls import Main as Cls
from person import Main as Person
class Main:
    def __init__(self):
        pass
    def __init__(self,data):
        self.terrainBank=Terrain(data).terrain_bank
        self.clsBank=Cls(data).cls_bank
        self.personBank=Person(data).person_bank