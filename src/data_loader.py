import os
import platform
import json
class Main:
    def __init__(self):
        ostype=platform.platform()
        path=os.getcwd()
        path=path[:-3]
        if ostype[:7]=="Windows":
            path=path+"data\\"
        else:
            path=path+"data/"
        #print(path)
        self.terrain_typenames=json.load(open(path+"terrain_typenames.json","r"))
        self.cls_group_typenames=json.load(open(path+"cls_group_typenames.json","r"))
        self.battle_enhance_typenames=json.load(open(path+"battle_enhance_typenames.json","r"))
        self.cls_typenames=json.load(open(path+"cls_typenames.json","r"))
        self.move_decay = json.load(open(path + "terrain_move_decay.json", "r"))
        self.terrain_battle_enhance=json.load(open(path+"terrain_battle_enhance.json","r"))
        self.cls_weapon_rank=json.load(open(path+"cls_weapon_rank.json","r"))
        self.cls_clsgroup=json.load(open(path+"cls_clsgroup.json","r"))
        self.cls_skills=json.load(open(path+"cls_skills.json","r"))
        self.cls_ability_limit=json.load(open(path+"cls_ability_limit.json","r"))
        self.persondata=json.load(open(path+"person.json","r"))
        self.pidlist=self.persondata.keys()
        self.terrain_map=json.load(open(path+"terrain_map_test.json","r"))
        self.map_armylist=json.load(open(path+"map_armylist_test.json","r"))
        self.item_type_list=json.load(open(path+"item_type_list.json","r"))
        self.init_item_list=json.load(open(path+"init_item_list.json","r"))
        self.support_cube=json.load(open(path+"support_cube.json","r"))
        self.attackable_weapon_types = json.load(open(path + "attackable_weapon_types.json", "r"))

