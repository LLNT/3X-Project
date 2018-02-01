import collections
import person
import item
import map_controller
from typing import List,Set,Dict

def wp_buf_count(wpa,wpd):
    if (wpa=="Sword"):
        if (wpd=="Axe"):
            return 1
        if (wpd=="Lance"):
            return -1
        return 0
    if (wpa=="Lance"):
        if (wpd=="Sword"):
            return 1
        if (wpd=="Axe"):
            return -1
        return 0
    if (wpa=="Axe"):
        if (wpd=="Lance"):
            return 1
        if (wpd=="Sword"):
            return -1
        return 0
    if (wpa=="Fire"):
        if (wpd=="Light")or(wpd=="Wind"):
            return 1
        if (wpd=="Dark")or(wpd=="Thunder"):
            return -1
        return 0
    if (wpa=="Thunder"):
        if (wpd=="Light")or(wpd=="Fire"):
            return 1
        if (wpd=="Dark")or(wpd=="Wind"):
            return -1
        return 0
    if (wpa=="Wind"):
        if (wpd=="Light")or(wpd=="Thunder"):
            return 1
        if (wpd=="Dark")or(wpd=="Fire"):
            return -1
        return 0
    if (wpa=="Light"):
        if (wpd=="Dark"):
            return 1
        if (wpd=="Fire")or(wpd=="Thunder")or(wpd=="Wind"):
            return -1
        return 0
    if (wpa=="Dark"):
        if (wpd=="Fire")or(wpd=="Thunder")or(wpd=="Wind"):
            return 1
        if (wpd=="Light"):
            return -1
        return 0
    return 0


class Attack:
    def __init__(self):
        self.AorD=0                  #type:int
        self.continued_attack=0      #type:int
        self.wea_dup_attack=0        #type:int
        self.shootingstar_attack=0   #type:int
        self.sky_ecl_attack=0        #type:int
        self.moonlight_attack=0      #type:int
        self.combo_bonus=1           #type:int
    def __init__(self,a,cn,wd,sh,se,ml,cb):
        self.AorD=a
        self.continued_attack=cn
        self.wea_dup_attack=wd
        self.shootingstar_attack=sh
        self.sky_ecl_attack=se
        self.moonlight_attack=ml
        self.combo_bonus=cb

class Battle:
    def __init__(self):
        self.queue=collections.deque([])  #type:collections.deque[Attack]
        self.dist=0                       #type:int
        self.wear_buf_a=0                 #type:int
        self.wear_buf_d=0                 #type:int
        self.exp_buf_a=0                  #type:int
        self.exp_buf_d=0                  #type:int
        self.charged_combat=0             #type:int
        self.att_sun=0                    #type:int
        self.att_moon=0                   #type:int
        self.att_wrath=0                  #type:int
        self.att_sup_eff=0                #type:int
        self.att_promised=0               #type:int
        self.att_crt=0                    #type:int
        self.att_shield=0                 #type:int
        self.bspd_a=0                     #type:int
        self.bspd_d=0                     #type:int
        self.wp_buf_a=0                   #type:int
        self.wp_buf_d=0                   #type:int
        self.weapon_a=None               #type:item.Item
        self.weapon_d=None               #type:item.Item
        self.weapon_rank_buf_a=0          #type:int
        self.weapon_rank_buf_d=0          #type:int
        self.skills_a=set([])             #type:Set[str]
        self.skills_d=set([])             #type:Set[str]
        self.battleround=0                #type:int
        self.su_a={}                      #type:Dict[str,int]
        self.su_d={}                      #type:Dict[str,int]
        self.a=None                      #type:person.Person
        self.d=None                      #type:person.Person
        self.hita=0                       #type:int
        self.hitd=0                       #type:int
        self.crta=0                       #type:int
        self.crtd=0                       #type:int
        self.atka=0                       #type:int
        self.atkd=0                       #type:int
        self.craa=0                       #type:int
        self.crad=0                       #type:int
        self.avoa=0                       #type:int
        self.avod=0                       #type:int
        self.defa=0                       #type:int
        self.defd=0                       #type:int
    def __init__(self,_a,_d,_wpa,_wpd,_map):
        self.queue = collections.deque([])  # type:collections.deque[Attack]
        self.a=_a                        #type:person.Person
        self.d=_d                        #type:person.Person
        map=_map                         #type:map_controller.Main
        self.weapon_a=_wpa               #type:item.Item
        self.weapon_d=_wpd               #type:item.Item
        posa=map.person_container.position[self.a.pid]
        posd=map.person_container.position[self.d.pid]
        self.dist=abs(posa[0]-posd[0])+abs(posa[1]-posd[1])
        self.exp_buf_a=self.a.ability["EXP"]
        self.exp_buf_d=self.d.ability["EXP"]
        self.wp_buf_a=0
        self.wp_buf_d=0
        self.battleround=0
        self.att_sun=0
        self.att_moon=0
        self.att_wrath=0
        self.att_sup_eff=0
        self.att_promised=0
        self.crt=0
        self.att_shield=0
        self.charged_combat=0
        if (self.weapon_d==None):
            self.battleround=1
        else:
            if (self.weapon_d.itemtype.max_range<self.dist):
                self.battleround=1
            if (self.weapon_d.itemtype.min_range>self.dist):
                self.battleround=1
        if (self.battleround==0):
            self.wp_buf_a=wp_buf_count(self.weapon_a.itemtype.weapontype,self.weapon_d.itemtype.weapontype)
        self.wp_buf_d=-self.wp_buf_a
        self.weapon_rank_buf_a=self.a.weapon_rank[self.weapon_a.itemtype.weapontype]
        if (self.battleround==0):
            self.weapon_rank_buf_d=self.d.weapon_rank[self.weapon_d.itemtype.weapontype]
        else:
            self.weapon_rank_buf_d=0
        self.wear_buf_a=self.weapon_a.use
        if (self.battleround==0):
            self.wear_buf_d=self.weapon_d.use
        else:
            self.wear_buf_d=0
        self.skills_a=set([])
        self.skills_d=set([])
        for item in self.a.skills:
            self.skills_a.add(item)
        for item in map.global_vars.clsBank[self.a.cls].cls_skills:
            self.skills_a.add(item)
        for item in self.weapon_a.itemtype.skills:
            self.skills_a.add(item)
        for item in self.d.skills:
            self.skills_d.add(item)
        for item in map.global_vars.clsBank[self.d.cls].cls_skills:
            self.skills_d.add(item)
        if not (self.weapon_d==None):
            for item in self.weapon_d.itemtype.skills:
                self.skills_d.add(item)
        aw_a=0
        aw_d=0
        if ("Awareness" in self.skills_a):
            aw_a=1
        if ("Awareness" in self.skills_d):
            aw_d=1
        if (aw_a==1):
            self.skills_d.clear()
        if (aw_d==1):
            self.skills_a.clear()
        self.bspd_a=self.a.ability["SPD"]
        self.bspd_d=self.d.ability["SPD"]
        if (self.weapon_a.itemtype.weight>self.a.ability["BLD"]):
            self.bspd_a+=(self.a.ability["BLD"]-self.weapon_a.itemtype.weight)
        if not (self.weapon_d==None):
            if (self.weapon_d.itemtype.weight>self.d.ability["BLD"]):
                self.bspd_d+=(self.d.ability["BLD"]-self.weapon_d.itemtype.weight)
        self.su_a=[]
        self.su_d=[]
        self.su_a=map.terrain_container.map[posa[0]][posa[1]].enhance[map.global_vars.cls_clsgroup[self.a.cls]].copy()
        self.su_d=map.terrain_container.map[posd[0]][posd[1]].enhance[map.global_vars.cls_clsgroup[self.d.cls]].copy()
        (self.hita,self.hitd,self.avoa,self.avod,self.crta,self.crtd,
         self.craa,self.crad,self.atka,self.atkd,self.defa,self.defd)=self.calc_param()

    def calc_param(self):
        self.hita=0
        self.hitd=0
        self.avod=0
        self.avoa=0
        self.atkd=0
        self.atka=0
        self.defa=0
        self.defd=0
        self.crtd=0
        self.crta=0
        self.crad=0
        self.craa=0
        self.hita=self.a.ability["SKL"]*2+self.a.ability["LUK"]+self.weapon_a.itemtype.hit+\
                  self.su_a["HIT"]+10*self.wp_buf_a
        self.avod=self.d.ability["SPD"]*2+self.d.ability["LUK"]+self.su_d["AVO"]
        self.crta=int(self.a.ability["SKL"]/2)+int(self.a.ability["LUK"]/4)+\
                  self.weapon_a.itemtype.critical+self.su_a["CRT"]
        self.crad=int(self.d.ability["LUK"]/2)+int(self.d.ability["SPD"]/4)+\
                  int(self.d.ability["SKL"]/4)+self.su_d["CRA"]
        if (self.weapon_a.itemtype.weapontype=="Sword")or(self.weapon_a.itemtype.weapontype=="Lance")or\
           (self.weapon_a.itemtype.weapontype=="Axe")or(self.weapon_a.itemtype.weapontype=="Bow"):
            self.atka=self.a.ability["STR"]
            self.defd=self.d.ability["DEF"]
        if (self.weapon_a.itemtype.weapontype=="Fire")or(self.weapon_a.itemtype.weapontype=="Thunder")or\
           (self.weapon_a.itemtype.weapontype=="Wind")or(self.weapon_a.itemtype.weapontype=="Light")or\
           (self.weapon_a.itemtype.weapontype=="Dark"):
            self.atka=self.a.ability["MGC"]
            self.defd=self.d.ability["RES"]
        self.atka+=(self.weapon_a.itemtype.power+self.su_a["ATK"]+self.wp_buf_a)
        self.defd+=self.su_d["DEF"]
        if self.battleround==0:
            self.hitd = self.d.ability["SKL"] * 2 + self.d.ability["LUK"] + self.weapon_d.itemtype.hit + \
                        self.su_d["HIT"] + 10 * self.wp_buf_d
            self.avoa = self.a.ability["SPD"] * 2 + self.a.ability["LUK"] + self.su_a["AVO"]
            self.crtd = int(self.d.ability["SKL"] / 2) + int(self.d.ability["LUK"] / 4) + \
                        self.weapon_d.itemtype.critical + self.su_d["CRT"]
            self.craa = int(self.a.ability["LUK"] / 2) + int(self.a.ability["SPD"] / 4) + \
                        int(self.a.ability["SKL"] / 4) + self.su_a["CRA"]
            if (self.weapon_d.itemtype.weapontype == "Sword") or (self.weapon_d.itemtype.weapontype == "Lance") or \
                    (self.weapon_d.itemtype.weapontype == "Axe") or (self.weapon_d.itemtype.weapontype == "Bow"):
                self.atkd = self.d.ability["STR"]
                self.defa = self.a.ability["DEF"]
            if (self.weapon_d.itemtype.weapontype == "Fire") or (self.weapon_d.itemtype.weapontype == "Thunder") or \
                    (self.weapon_d.itemtype.weapontype == "Wind") or (self.weapon_d.itemtype.weapontype == "Light") or \
                    (self.weapon_d.itemtype.weapontype == "Dark"):
                self.atkd = self.d.ability["MGC"]
                self.defa = self.a.ability["RES"]
            self.atkd += (self.weapon_d.itemtype.power + self.su_d["ATK"] + self.wp_buf_d)
            self.defa += self.su_a["DEF"]
        if ("Promised" in self.skills_d):
            self.crta=-65536
        if ("Whiteseal" in self.skills_a):
            self.hita=65536
            self.defd=int(self.defd/2)
        if ("Blackseal" in self.skills_d):
            self.atka=int(self.atka/2)
        if ("Greenseal" in self.skills_d):
            self.hita=int(self.hita/2)
        if ("Blueseal" in self.skills_a):
            self.crad=0
            self.crta=2*self.crta
        if (self.battleround==0):
            if ("Promised" in self.skills_a):
                self.crtd=-65536
            if ("Whiteseal" in self.skills_d):
                self.hitd=65536
                self.defa=int(self.defa/2)
            if ("Blackseal" in self.skills_a):
                self.atkd=int(self.atkd/2)
            if ("Greenseal" in self.skills_a):
                self.hitd=int(self.hitd/2)
            if ("Blueseal" in self.skills_d):
                self.craa=0
                self.crtd=2*self.crtd
        return (self.hita,self.hitd,self.avoa,self.avod,self.crta,self.crtd,
                 self.craa,self.crad,self.atka,self.atkd,self.defa,self.defd)

    def simulate(self):
        hita=self.hita-self.avod
        crta=self.crta-self.crad
        dmga=self.atka-self.defd
        if (hita>100):
            hita=100
        if (hita<0):
            hita=0
        if (crta>100):
            crta=100
        if (crta<0):
            crta=0
        if (dmga<0):
            dmga=0
        if (self.bspd_a-self.bspd_d>=4):
            pura=1
        else:
            pura=0
        sup_a=self.wp_buf_a
        b_r=self.battleround
        if b_r==1:
            return (b_r,sup_a,pura,hita,crta,dmga,0,0,0,0,0)
        hitd=self.hitd-self.avoa
        crtd=self.crtd-self.craa
        dmgd=self.atkd-self.defa
        if (hitd>100):
            hitd=100
        if (hitd<0):
            hitd=0
        if (crtd>100):
            crtd=100
        if (crtd<0):
            crtd=0
        if (dmgd<0):
            dmgd=0
        if (self.bspd_d-self.bspd_a>=4):
            purd=1
        else:
            purd=0
        sup_d=self.wp_buf_d
        return (b_r,sup_a,pura,hita,crta,dmga,sup_d,purd,hitd,crtd,dmgd)
        # b_r    0: 有反击 1: 没反击
        # sup_a  0: 普通  1: 有利  -1:不利
        # pura   0: 不能追击 1: 可以追击
        # hita   命中率
        # crta   必杀率
        # dmga   伤害








