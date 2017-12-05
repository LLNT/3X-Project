from terrain import Main as Terrain
from cls import Main as Cls
class Main:
    def __init__(self):
        self.terrainBank=Terrain().terrain_bank
        self.clsBank=Cls().cls_bank
    def __init__(self,data):
        self.terrainBank=Terrain(data).terrain_bank
        self.clsBank=Cls(data).cls_bank