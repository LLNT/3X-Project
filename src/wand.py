from . import person,map_controller,item
import random
from typing import List,Tuple
from .utility import *

class Wand:
    def __init__(self):
        self.p=None #type:person.Person
        self.wand=None #type:item.Item
        self.map=None #type:map_controller.Main
        self.exp_buf=0 #type:int
        self.obj=None #type:person.Person

    def get_battlecard(self):
        if self.obj==None:
            return (self.p.battlecard[self.p.cls]["Base"],None)
        else:
            return (self.p.battlecard[self.p.cls]["Base"],self.obj.battlecard[self.obj.cls]["Base"])

class Type0(Wand):
    def __init__(self):
        super(Type0,self).__init__()
        self.log=[] #type:List[str]
    def __init__(self,p,wand,obj,map):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.obj=obj  #type:person.Person
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
    def execute(self):
        funcs=self.wand.itemtype.wand["Effect"].split(",")
        for func in funcs:
            if func=="HEAL":
                base=self.wand.itemtype.power+self.p.ability["MGC"]
                hpdiff=self.obj.ability["MHP"]-self.obj.ability["HP"]
                if base>hpdiff:
                    base=hpdiff
                self.obj.ability["HP"]+=base
                self.log.append((1,"H,%d,0"%(base)))
            if func=="RELIEF":
                if "Sleep" in self.obj.status:
                    self.obj.status.pop("Sleep")
                    self.log.append((-1, "Relief Sleep"))
                if "Stone" in self.obj.status:
                    self.obj.status.pop("Stone")
                    self.log.append((-1, "Relief Stone"))
                if "Berserk" in self.obj.status:
                    self.obj.status.pop("Berserk")
                    self.log.append((-1, "Relief Berserk"))
                if "Poison" in self.obj.status:
                    self.obj.status.pop("Poison")
                    self.log.append((-1, "Relief Poison"))
                if "Silence" in self.obj.status:
                    self.obj.status.pop("Silence")
                    self.log.append((-1, "Relief Silence"))
            if func=="POWER":
                self.obj.ability["MGC"]+=7
                self.obj.add_status("Power",7)
                self.log.append((-1,"Powered"))
            if func=="RESTORE":
                self.obj.ability["DEF"]+=7
                self.obj.add_status("Restore",7)
                self.log.append((-1,"Restored"))
            if func=="BARRIER":
                self.obj.ability["RES"]+=7
                self.obj.add_status("Barrier",7)
                self.log.append((-1,"Barriered"))
            if func=="PROTECT":
                self.obj.add_status("Immortal",1)
                self.log.append((-1,"Protected"))
        self.p.weapon_rank["Wand"]+=self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"]>=400:
            self.p.weapon_rank["Wand"]=400
        self.exp_buf+=int((self.wand.itemtype.rank+50)/4)
        if not(self.wand.itemtype.infinite==1):
            self.wand.use-=1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple

class Type1(Wand):
    def __init__(self):
        super(Type1,self).__init__()
        self.log=[] #type:List[str]
        self.pos=(0,0) #type:Tuple[int,int]
        self.hit=0
        self.avo=0
        self.dist=0
    def __init__(self,p,wand,obj,map,pos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.obj=obj  #type:person.Person
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.pos=pos #type:Tuple[int,int]
        self.hit=0     #type:int
        self.avo=0     #type:int
        self.dist=calc_dist(self.pos,self.map.person_container.position[self.obj.pid])
        self.hit+=self.wand.itemtype.hit
        self.hit+=self.p.ability["MGC"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
        self.hit+=self.p.ability["SKL"]
        self.avo+=self.obj.ability["RES"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
    def simulate(self):
        sim_hit=self.hit-self.avo
        sim_hit+=(11-self.dist)
        if sim_hit<0:
            sim_hit=0
        return sim_hit
    def execute(self):
        sim_hit = self.hit - self.avo
        sim_hit += (11 - self.dist)
        q=random.randint(0,99)
        if q<sim_hit:
            funcs=self.wand.itemtype.wand["Effect"].split(",")
            for func in funcs:
                if func=="BERSERK":
                    self.obj.add_status("Berserk", 5)
                    self.log.append((-1, "Berserk"))
                if func=="SLEEP":
                    self.obj.add_status("Sleep", 5)
                    self.log.append((-1, "Sleep"))
                if func=="SILENCE":
                    self.obj.add_status("Silence", 5)
                    self.log.append((-1, "Silence"))
                if func=="STONE":
                    self.obj.add_status("Stone", 5)
                    self.log.append((-1, "Stone"))
                if func=="POISON":
                    self.obj.add_status("Poison", 5)
                    self.log.append((-1, "Poison"))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
            if not (self.wand.itemtype.infinite == 1):
                self.wand.use -= 1
            if self.wand.use <= 0:
                self.p.banish(self.wand)
                self.log.append((-1, "Wand used out"))
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple
        else:
            self.log.append((-1,"Miss"))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += 1
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple

class Type2(Wand):
    def __init__(self):
        super(Type2,self).__init__()
        self.log=[] #type:List[str]
        self.item_to_repair=None #type:item.Item
    def __init__(self,p,wand,obj,map,_item):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.obj=obj  #type:person.Person
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.item_to_repair=_item #type:item.Item
    def execute(self):
        funcs=self.wand.itemtype.wand["Effect"].split(",")
        for func in funcs:
            if func=="REPAIR":
                max_use=self.item_to_repair.itemtype.max_use
                self.item_to_repair.use=max_use
                self.log.append((-1,"Item repaired"))
        self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"] >= 400:
            self.p.weapon_rank["Wand"] = 400
        self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
        if not (self.wand.itemtype.infinite == 1):
            self.wand.use -= 1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple

class Type3(Wand):
    def __init__(self):
        super(Type3,self).__init__()
        self.log=[] #type:List[str]
        self.pos=(0,0) #type:Tuple[int,int]
        self.hit=0
        self.avo=0
        self.dist=0
        self.item_to_get=None #type:item.Item
    def __init__(self,p,wand,obj,map,pos,_item):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.obj=obj  #type:person.Person
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.pos=pos #type:Tuple[int,int]
        self.hit=0     #type:int
        self.avo=0     #type:int
        self.item_to_get=_item #type:item.Item
        self.dist=calc_dist(self.pos,self.map.person_container.position[self.obj.pid])
        self.hit+=self.wand.itemtype.hit
        self.hit+=self.p.ability["MGC"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
        self.hit+=self.p.ability["SKL"]
        self.avo+=self.obj.ability["RES"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
    def simulate(self):
        sim_hit=self.hit-self.avo
        sim_hit+=(11-self.dist)
        if sim_hit<0:
            sim_hit=0
        return sim_hit
    def execute(self):
        sim_hit = self.hit - self.avo
        sim_hit += (11 - self.dist)
        q=random.randint(0,99)
        if q<sim_hit:
            funcs=self.wand.itemtype.wand["Effect"].split(",")
            for func in funcs:
                if func=="THIEF":
                    self.obj.dequip(self.item_to_get)
                    self.obj.item.remove(self.item_to_get)
                    self.log.append((-1, "Getitem"))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
            if not (self.wand.itemtype.infinite == 1):
                self.wand.use -= 1
            if self.wand.use <= 0:
                self.p.banish(self.wand)
                self.log.append((-1, "Wand used out"))
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple
        else:
            self.log.append((-1,"Miss"))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += 1
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple

class Type4(Wand):
    def __init__(self):
        super(Type4,self).__init__()
        self.log=[] #type:List[str]
        self.tarpos=(0,0) #type:Tuple[int,int]
    def __init__(self,p,wand,map,tarpos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.tarpos=tarpos #type:Tuple[int,int]
        self.obj=None
    def execute(self):
        funcs=self.wand.itemtype.wand["Effect"].split(",")
        for func in funcs:
            if func=="REWARP":
                self.map.person_container.position[self.p.pid]=self.tarpos
                self.log.append((-1,"%s Moved"%(self.p.name)))
            if func=="TORCH":
                pass
            if func=="UNLOCK":
                pass
        self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"] >= 400:
            self.p.weapon_rank["Wand"] = 400
        self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
        if not (self.wand.itemtype.infinite == 1):
            self.wand.use -= 1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple

class Type5(Wand):
    def __init__(self):
        super(Type5,self).__init__()
        self.log=[] #type:List[str]
        self.pos=(0,0) #type:Tuple[int,int]
        self.hit=0
        self.avo=0
        self.dist=0
        self.tarpos=(0,0)
    def __init__(self,p,wand,obj,map,pos,tarpos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.obj=obj  #type:person.Person
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.pos=pos #type:Tuple[int,int]
        self.hit=0     #type:int
        self.avo=0     #type:int
        self.tarpos=tarpos
        self.dist=calc_dist(self.pos,self.map.person_container.position[self.obj.pid])
        self.hit+=self.wand.itemtype.hit
        self.hit+=self.p.ability["MGC"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
        self.hit+=self.p.ability["SKL"]
        self.avo+=self.obj.ability["RES"]*2
        self.hit+=int(self.p.ability["LUK"]/2)
    def simulate(self):
        sim_hit=self.hit-self.avo
        sim_hit+=(11-self.dist)
        if sim_hit<0:
            sim_hit=0
        return sim_hit
    def execute(self):
        sim_hit = self.hit - self.avo
        sim_hit += (11 - self.dist)
        q=random.randint(0,99)
        if q<sim_hit:
            funcs=self.wand.itemtype.wand["Effect"].split(",")
            for func in funcs:
                if func=="EXPEL":
                    self.map.person_container.position[self.obj.pid] = self.tarpos
                    self.log.append((-1, "%s Moved" % (self.obj.name)))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
            if not (self.wand.itemtype.infinite == 1):
                self.wand.use -= 1
            if self.wand.use <= 0:
                self.p.banish(self.wand)
                self.log.append((-1, "Wand used out"))
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple
        else:
            self.log.append((-1,"Miss"))
            self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
            if self.p.weapon_rank["Wand"] >= 400:
                self.p.weapon_rank["Wand"] = 400
            self.exp_buf += 1
            ori_abl = self.p.ability.copy()
            growthtuple = [1, 0, 0, {}, {}]
            if not self.map.person_container.controller[self.p.pid] == 0:
                return self.log, growthtuple
            self.p.ability["EXP"] += self.exp_buf
            lv_up = 0
            while self.p.ability["EXP"] >= 100:
                lv_up += 1
                self.p.ability["EXP"] -= 100
            if (lv_up + self.p.ability["LV"] >= 20):
                lv_up = 20 - self.p.ability["LV"]
                self.p.ability["EXP"] = 0
            growthlist = []
            for i in range(lv_up):
                growth = self.p.lv_up()
                growthlist.append(growth)
            growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist, ori_abl]
            return self.log, growthtuple

class Type6(Wand):
    def __init__(self):
        super(Type6,self).__init__()
        self.log=[] #type:List[str]
        self.pos=(0,0) #type:Tuple[int,int]
        self.tarpos=(0,0)
    def __init__(self,p,wand,obj,map,pos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.obj=obj   #type:person.Person
        self.pos=pos #type:Tuple[int,int]
        self.tarpos=self.map.find_nearest_empty_block(self.pos,[self.map.person_container.position[self.p.pid]],[self.pos])
    def get_target(self):
        return self.tarpos
    def execute(self):
        funcs=self.wand.itemtype.wand["Effect"].split(",")
        for func in funcs:
            if func=="RESCUE":
                self.map.person_container.position[self.obj.pid]=self.tarpos
                self.log.append((-1,"%s Moved"%(self.obj.name)))
        self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"] >= 400:
            self.p.weapon_rank["Wand"] = 400
        self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
        if not (self.wand.itemtype.infinite == 1):
            self.wand.use -= 1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple

class Type7(Wand):
    def __init__(self):
        super(Type7,self).__init__()
        self.log=[] #type:List[str]
        self.tarpos=(0,0) #type:Tuple[int,int]
    def __init__(self,p,wand,obj,map,tarpos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.obj=obj   #type:person.Person
        self.tarpos=tarpos #type:Tuple[int,int]
    def execute(self):
        funcs=self.wand.itemtype.wand["Effect"].split(",")
        for func in funcs:
            if func=="WARP":
                self.map.person_container.position[self.obj.pid]=self.tarpos
                self.log.append((-1,"%s Moved"%(self.obj.name)))
        self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"] >= 400:
            self.p.weapon_rank["Wand"] = 400
        self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
        if not (self.wand.itemtype.infinite == 1):
            self.wand.use -= 1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple

class Type8(Wand):
    def __init__(self):
        super(Type8,self).__init__()
        self.log=[] #type:List[str]
        self.pos=(0,0)
    def __init__(self,p,wand,map,pos):
        self.p=p  #type:person.Person
        self.wand=wand  #type:item.Item
        self.map=map  #type:map_controller.Main
        self.log=[]   #type:List[str]
        self.exp_buf=0 #type:int
        self.pos=pos
        self.obj=None
    def get_objs(self):
        obj=[]
        minr=self.wand.itemtype.min_range
        maxr=self.wand.itemtype.max_range
        if maxr==-1:
            maxr=self.p.ability["MGC"]
        if maxr<minr:
            maxr=minr
        for _obj in self.map.person_container.position:
            if (calc_dist(self.pos,self.map.person_container.position[_obj])<=maxr) and \
                (calc_dist(self.pos,self.map.person_container.position[_obj])>=minr):
                if (self.map.person_container.controller[self.p.pid]%2==self.map.person_container.controller[_obj]%2):
                    obj.append(self.map.global_vars.personBank[_obj])
        return obj
    def execute(self):
        objs=self.get_objs()
        for obj in objs:
            funcs=self.wand.itemtype.wand["Effect"].split(",")
            for func in funcs:
                if func=="HEAL":
                    base=self.wand.itemtype.power+self.p.ability["MGC"]
                    hpdiff=obj.ability["MHP"]-obj.ability["HP"]
                    if base>hpdiff:
                        base=hpdiff
                    obj.ability["HP"]+=base
                    self.log.append((1,"H,%d,0"%(base)))
                if func=="RELIEF":
                    if "Sleep" in obj.status:
                        obj.status.pop("Sleep")
                        self.log.append((-1, "Relief Sleep"))
                    if "Stone" in obj.status:
                        obj.status.pop("Stone")
                        self.log.append((-1, "Relief Stone"))
                    if "Berserk" in obj.status:
                        obj.status.pop("Berserk")
                        self.log.append((-1, "Relief Berserk"))
                    if "Poison" in obj.status:
                        obj.status.pop("Poison")
                        self.log.append((-1, "Relief Poison"))
                    if "Silence" in obj.status:
                        obj.status.pop("Silence")
                        self.log.append((-1, "Relief Silence"))
        self.p.weapon_rank["Wand"] += self.wand.itemtype.weapexp
        if self.p.weapon_rank["Wand"] >= 400:
            self.p.weapon_rank["Wand"] = 400
        self.exp_buf += int((self.wand.itemtype.rank + 50) / 4)
        if not (self.wand.itemtype.infinite == 1):
            self.wand.use -= 1
        if self.wand.use<=0:
            self.p.banish(self.wand)
            self.log.append((-1,"Wand used out"))
        ori_abl=self.p.ability.copy()
        growthtuple=[1,0,0,{},{}]
        if not self.map.person_container.controller[self.p.pid]==0:
            return self.log,growthtuple
        self.p.ability["EXP"] += self.exp_buf
        lv_up = 0
        while self.p.ability["EXP"] >= 100:
            lv_up += 1
            self.p.ability["EXP"] -= 100
        if (lv_up + self.p.ability["LV"] >= 20):
            lv_up = 20 - self.p.ability["LV"]
            self.p.ability["EXP"] = 0
        growthlist = []
        for i in range(lv_up):
            growth = self.p.lv_up()
            growthlist.append(growth)
        growthtuple = [1, lv_up, self.p.ability["EXP"], growthlist,ori_abl]
        return self.log,growthtuple
