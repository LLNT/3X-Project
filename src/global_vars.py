from typing import Dict, List
import terrain
import cls
import person
import ai_controller
import itemtype
import item
class Main:
    def __init__(self):
        self.terrainBank={}                 #type:Dict[str,terrain.Terrain]
        self.clsBank={}                     #type:Dict[str,cls.Cls]
        self.personBank={}                  #type:Dict[str,person.Person]
        self.cls_clsgroup={}                #type:Dict[str,str]
        self.AIcontroller=None             #type:ai_controller.AI_Controller
        self.itemtypeBank={}                #type:Dict[str,itemtype.Itemtype]
        self.itemBank={}                    #type:Dict[int,item.Item]
        self.support_cube={}                #type:Dict[str,Dict[str,Dict[str,int]]]
        self.attackable_weapon_types=[]     #type:List[str]
        self.player_character_status={}     #type:Dict[str,int]
        self.cls_rank={}                    #type:Dict[str,List[str]]
        self.flags={}                       #type:Dict[str,bool]
        self.transporter={}                 #type:Dict[str,List[item.Item]]
        self.cls_promotion={}               #type:Dict[str,Dict[str,int]]
        self.support_text_map={}            #type:Dict[str,Dict[str,Dict[str,List[str]]]]
        self.text={}                        #type:Dict[str,Dict[str,str]]
        self.ai_configs={}
    def __init__(self,data):
        self.terrainBank=terrain.Main(data).terrain_bank
        self.clsBank=cls.Main(data).cls_bank
        self.itemtypeBank = itemtype.Main(data).itemtype_bank
        self.itemBank=item.Main(data,self.itemtypeBank).item_bank
        self.personBank=person.Main(data,self.itemBank).person_bank
        self.cls_clsgroup=data.cls_clsgroup
        self.AIcontroller=ai_controller.AI_Controller()
        self.support_cube=data.support_cube
        self.attackable_weapon_types=data.attackable_weapon_types
        self.player_character_status=data.player_character_init
        self.cls_rank=data.cls_rank
        self.flags=data.flags
        self.transporter={}
        for _type in data.itemtype_typenames:
            self.transporter[_type]=[]
        self.cls_promotion=data.cls_promote_bonus
        self.support_text_map=data.support_text_map
        self.text=data.text
        self.ai_configs=data.ai_configs

