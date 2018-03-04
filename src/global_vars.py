from typing import Dict, List
import terrain
import cls
import person
import ai_controller
import itemtype
import item
import data_loader
import terrain_container
import person_container
import map_controller
import pickle

class Main:
    def __init__(self):
        self.terrainBank={}                 #type:Dict[str,terrain.Terrain]
        self.clsBank={}                     #type:Dict[str,cls.Cls]
        self.personBank={}                  #type:Dict[str,person.Person]
        self.AIcontroller=None             #type:ai_controller.AI_Controller
        self.itemtypeBank={}                #type:Dict[str,itemtype.Itemtype]
        self.itemBank={}                    #type:Dict[int,item.Item]
        self.player_character_status={}     #type:Dict[str,int]
        self.flags={}                       #type:Dict[str,bool]
        self.transporter={}                 #type:Dict[str,List[item.Item]]
        self.maps=[]
        self.data=None                     #type:data_loader.Main
    def __init__(self,data):
        self.terrainBank=terrain.Main(data).terrain_bank
        self.clsBank=cls.Main(data).cls_bank
        self.itemtypeBank = itemtype.Main(data).itemtype_bank
        self.itemBank=item.Main(data,self.itemtypeBank).item_bank
        self.personBank=person.Main(data,self.itemBank).person_bank
        self.AIcontroller=ai_controller.AI_Controller()
        self.player_character_status=data.player_character_init
        self.flags=data.flags
        self.transporter={}
        self.data=data                     #type:data_loader.Main
        for _type in data.itemtype_typenames:
            self.transporter[_type]=[]
        self.maps=[]

    def new_game(self):
        terrain0=terrain_container.Main(self.data.get_obj(self.data.startmeta["Terrain_map"]), self.terrainBank)
        person0 = person_container.Main(self.data.get_obj(self.data.startmeta["Armylist"]),self.personBank, self.data.ai_configs)
        map0 = map_controller.Main(terrain0, person0, self,self.data.get_obj(self.data.startmeta["Eventlist"]))
        self.maps.append((map0,self.data.startmeta))
        self.flags=self.data.flags
        self.player_character_status=self.data.player_character_init
        self.transporter={}
        return map0

    def map_save(self,fname):
        path=self.data.get_root("save")
        obj=pickle.dump(self,open(path+fname,"wb"))
        return obj

    def map_load(self,fname):
        path=self.data.get_root("save")
        obj=pickle.load(open(path+fname,"rb"))
        map_active=obj.maps[-1]
        return map_active






