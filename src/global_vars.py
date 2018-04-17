from typing import Dict, List
import time
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
        self.gold=0
        self.settings = {}
        self.saved_time="19960229065033" #type:str
        self.saved_type=0   #type:int
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
        self.settings = data.settings
        for _type in data.itemtype_typenames:
            self.transporter[_type]=[]
        self.maps=[]
        self.gold=0
        self.saved_time=time.strftime("%Y%m%d%H%M%S",time.localtime())
        self.saved_type=0 #0 free save 1 after 2 preparation 3 prebattle

    def new_game(self):
        terrain0=terrain_container.Main(self.data.get_obj(self.data.startmeta["Terrain_map"]), self.terrainBank)
        person0 = person_container.Main(self.data.get_obj(self.data.startmeta["Armylist"]),self.personBank, self.data.ai_configs)
        map0 = map_controller.Main(terrain0, person0, self,[],self.data.get_obj(self.data.startmeta["Eventlist"]),
                                   self.data.get_obj(self.data.startmeta["Prelude"]),self.data.get_obj(self.data.startmeta["Afterscene"]),
                                   self.data.startmeta["Map_pic"],self.data.startmeta["Background_Scene"],
                                   self.data.startmeta["Title"],self.data.startmeta["Leader"])
        self.maps.append((map0,self.data.startmeta))
        self.flags=self.data.flags
        self.player_character_status=self.data.player_character_init
        self.transporter={}
        return map0

    @classmethod
    def saved_data_preload(cls,n=4):
        loaded_maps=[]
        for i in range(n):
            fname="game_%d.sav"%(i)
            try:
                premap=cls.map_load(fname)
            except FileNotFoundError:
                loaded_maps.append(None)
            else:
                loaded_maps.append(premap)
        return loaded_maps

    def map_save(self,fname,t=0):
        self.saved_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.saved_type=t
        path=self.data.get_root("save")
        obj=pickle.dump(self,open(path+fname,"wb"))
        return obj

    @classmethod
    def map_load(cls,fname):
        path=data_loader.Main.get_root("save")
        obj=pickle.load(open(path+fname,"rb"))
        map_active=obj.maps[-1]
        return map_active

    def new_map(self,fname):
        meta=self.data.get_obj(fname)
        _terrain = terrain_container.Main(self.data.get_obj(meta["Terrain_map"]), self.terrainBank)
        _person = person_container.Main(self.data.get_obj(meta["Armylist"]), self.personBank,self.data.ai_configs)
        _map = map_controller.Main(_terrain, _person, self, [], self.data.get_obj(meta["Eventlist"]),
                                   self.data.get_obj(meta["Prelude"]),self.data.get_obj(meta["Afterscene"]),meta["Map_pic"],
                                   meta["Background_Scene"],meta["Title"],meta["Leader"])
        self.maps.append((_map, meta))
        return self.maps[-1]






