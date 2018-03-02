import os
import platform
import json
import codecs
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
        self.terrain_map=json.load(open(path+"terrain_map_0.json","r"))
        self.map_armylist=json.load(open(path+"map0_armylist.json","r"))
        self.item_type_list=json.load(open(path+"item_type_list.json","r"))
        self.init_item_list=json.load(open(path+"init_item_list.json","r"))
        self.support_cube=json.load(open(path+"support_cube.json","r"))
        self.attackable_weapon_types = json.load(open(path + "attackable_weapon_types.json", "r"))
        self.player_character_init=json.load(open(path+"player_character_init.json","r"))
        self.cls_rank=json.load(open(path+"cls_rank.json","r"))
        self.itemtype_typenames=json.load(open(path+"itemtype_typenames.json","r"))
        self.flags=json.load(open(path+"flags.json","r"))
        self.cls_promote_bonus=json.load(open(path+"cls_promotion_bonus.json","r"))
        self.support_text_map=json.load(open(path+"support_text.json","r"))
        self.text=json.load(codecs.open(path+"text.json","r","utf-8"))
        self.eventlist=json.load(open(path+"eventlist_map0.json","r"))
        self.ai_configs=json.load(open(path+"ai_configs.json","r"))
        self.startmeta=json.load(open(path+"map0_meta.json","r"))
    def get_obj(self,fname):
        ostype = platform.platform()
        path = os.getcwd()
        path = path[:-3]
        if ostype[:7] == "Windows":
            path = path + "data\\"
        else:
            path = path + "data/"
        return json.load(open(path+fname,"r"))
