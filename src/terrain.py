


class Terrain:
    def __init__(self):
        pass
    def __init__(self,typename,enhance,decay):
        self.typename=typename
        self.enhance=enhance#battle_enhance[self.typename]
        self.decay=decay#move_decay[self.typename]

class TerrainBank:
    def __init__(self):
        pass
    def __init__(self,typenamelist,enhance,decay):
        self.terrain_bank={}
        for typename in typenamelist:
            terrain=Terrain(typename,enhance[typename],decay[typename])
            self.terrain_bank[typename]=terrain

class Main:
    def __init__(self):
        typenamelist = list(["Plain", "Wood", "River", "Mountain", "High Mountain",
                             "Sea", "Forest", "Grass", "Bridge", "Column", "Wall",
                             "Avenue", "Cliff", "Gate", "Village", "Fort", "Throne"])
        battle_enhance = {}
        move_decay = {}
        base_enhance_vec = {"HIT": 0, "AVO": 0, "CRT": 0, "CRA": 0, "ATK": 0, "DEF": 0}
        for typename in typenamelist:
            temp = {"Infantry": base_enhance_vec, "Knight": base_enhance_vec}
            battle_enhance[typename] = temp
        move_decay["Plain"] = {"Infantry": 1, "Knight": 1}
        move_decay["Wood"] = {"Infantry": 2, "Knight": 3}
        move_decay["River"] = {"Infantry": 5, "Knight": 255}
        move_decay["Mountain"] = {"Infantry": 3, "Knight": 255}
        move_decay["High Mountain"] = {"Infantry": 255, "Knight": 255}
        move_decay["Sea"] = {"Infantry": 255, "Knight": 255}
        move_decay["Forest"] = {"Infantry": 5, "Knight": 255}
        move_decay["Grass"] = {"Infantry": 1, "Knight": 1.5}
        move_decay["Bridge"] = {"Infantry": 1, "Knight": 1}
        move_decay["Column"] = {"Infantry": 1, "Knight": 1.5}
        move_decay["Wall"] = {"Infantry": 255, "Knight": 255}
        move_decay["Avenue"] = {"Infantry": 1, "Knight": 0.8}
        move_decay["Cliff"] = {"Infantry": 255, "Knight": 255}
        move_decay["Gate"] = {"Infantry": 1, "Knight": 1}
        move_decay["Village"] = {"Infantry": 1, "Knight": 1}
        move_decay["Fort"] = {"Infantry": 1, "Knight": 1}
        move_decay["Throne"] = {"Infantry": 1, "Knight": 1}
        self.terrain_bank=TerrainBank(typenamelist,battle_enhance,move_decay).terrain_bank

