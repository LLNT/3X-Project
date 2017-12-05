import os
import json
class Main:
    def __init__(self):
        path=os.getcwd()
        path=path[:-3]
        path=path+"data\\"
        print(path)
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