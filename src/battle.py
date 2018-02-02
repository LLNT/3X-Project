import collections
import person
import item
import map_controller
import random
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
    def __init__(self,a,cn,wd,sh,se,ml):
        self.AorD=a
        self.continued_attack=cn
        self.wea_dup_attack=wd
        self.shootingstar_attack=sh
        self.sky_ecl_attack=se
        self.moonlight_attack=ml

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
        self.sup_eff_a=0                  #type:int
        self.sup_eff_d=0                  #type:int
        self.redseala=0                   #type:int
        self.redseald=0                   #type:int
        self.combo_bonusa=0               #type:int
        self.combo_bonusd=0               #type:int
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
        self.immortala=0                  #type:int
        self.immortald=0                  #type:int
        self.log=[]                       #type:List[Tuple[int,str]]
    def __init__(self,_a,_d,_wpa,_wpd,_map,posa):
        self.queue = collections.deque([])  # type:collections.deque[Attack]
        self.log = []                    #type:List[Tuple[int,str]]
        self.a=_a                        #type:person.Person
        self.d=_d                        #type:person.Person
        map=_map                         #type:map_controller.Main
        self.weapon_a=_wpa               #type:item.Item
        self.weapon_d=_wpd               #type:item.Item
        #posa=map.person_container.position[self.a.pid]
        posd=map.person_container.position[self.d.pid]
        self.dist=abs(posa[0]-posd[0])+abs(posa[1]-posd[1])
        self.exp_buf_a=self.a.ability["EXP"]
        self.exp_buf_d=self.d.ability["EXP"]
        self.wp_buf_a=0
        self.wp_buf_d=0
        self.battleround=0
        self.att_sun=0
        self.att_crt=0
        self.att_moon=0
        self.att_wrath=0
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
        self.immortala = 0
        self.immortald = 0
        if ("Immortal" in self.skills_a):
            self.immortala=0
        if ("Immortal" in self.skills_d):
            self.immortald=0
        if ("Awareness" in self.skills_a):
            aw_a=1
            self.log.append((-1,"Awareness"))
        if ("Awareness" in self.skills_d):
            aw_d=1
            self.log.append((-2,"Awareness"))
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
        self.sup_eff_a=0
        self.sup_eff_d=0
        if (map.global_vars.cls_clsgroup[self.d.cls] in self.weapon_a.itemtype.special_effect):
            self.sup_eff_a=1
        if (self.battleround==0):
            if (map.global_vars.cls_clsgroup[self.a.cls] in self.weapon_d.itemtype.special_effect):
                self.sup_eff_d=1
        self.redseala=0
        self.redseald=0
        self.combo_bonusa=1
        self.combo_bonusd=1
        if ("Redseal" in self.skills_a):
            self.log.append((-1,"Redseal"))
            self.redseala=1
        if ("Redseal" in self.skills_d):
            self.redseald=1
            self.log.append((-2,"Redseal"))
        self.calc_param(turns=0)

    def calc_param(self,turns=1):
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
        self.atka=self.atka*(1+self.sup_eff_a)
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
            self.atkd=self.atkd*(1+self.sup_eff_d)
            self.defa += self.su_a["DEF"]
        if ("Promised" in self.skills_d):
            if turns==0:
                self.log.append((-2,"Promised"))
            self.crta=-65536
        if ("Whiteseal" in self.skills_a):
            self.hita=65536
            self.defd=int(self.defd/2)
            if turns==0:
                self.log.append((-1,"Whiteseal"))
        if ("Blackseal" in self.skills_d):
            self.atka=int(self.atka/2)
            if turns == 0:
                self.log.append((-2,"Blackseal"))
        if ("Greenseal" in self.skills_d):
            self.hita=int(self.hita/2)
            if turns == 0:
                self.log.append((-2,"Greenseal"))
        if ("Blueseal" in self.skills_a):
            self.crad=0
            self.crta=2*self.crta
            if turns == 0:
                self.log.append((-1,"Blueseal"))
        if (self.battleround==0):
            if ("Promised" in self.skills_a):
                self.crtd=-65536
                if turns == 0:
                    self.log.append((-1,"Promised"))
            if ("Whiteseal" in self.skills_d):
                self.hitd=65536
                self.defa=int(self.defa/2)
                if turns == 0:
                    self.log.append((-2,"Whiteseal"))
            if ("Blackseal" in self.skills_a):
                self.atkd=int(self.atkd/2)
                if turns == 0:
                    self.log.append((-1,"Blackseal"))
            if ("Greenseal" in self.skills_a):
                self.hitd=int(self.hitd/2)
                if turns == 0:
                    self.log.append((-1,"Greenseal"))
            if ("Blueseal" in self.skills_d):
                self.craa=0
                self.crtd=2*self.crtd
                if turns == 0:
                    self.log.append((-2,"Blueseal"))
        return

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

    def battle(self):
        if (self.battleround==0):
            r=self.battlea()
            self.weapon_a.use = self.wear_buf_a
            if self.weapon_a.use == 0:
                print("WARNING A RUNS OUT OF WEAPON")
            self.weapon_d.use = self.wear_buf_d
            if self.weapon_d.use == 0:
                print("WARNING D RUNS OUT OF WEAPON")
            if (r == 1):
                print("WARNING D IS DEFEATED")
            if (r == 2):
                print("WARNING A IS DEFEATED")
            return self.log
        else:
            r=self.battleb()
            self.weapon_a.use=self.wear_buf_a
            if self.weapon_a.use==0:
                print("WARNING A RUNS OUT OF WEAPON")
            if (r==1):
                print("WARNING D IS DEFEATED")
            if (r==2):
                print("WARNING A IS DEFEATED")
            return self.log


    def ambush_a(self):
        if not("Ambush" in self.skills_a):
            return 0
        if (self.a.ability["HP"]>int(self.a.ability["MHP"]/2)):
            return 0
        if (self.bspd_a*1.5<self.bspd_d):
            return 0
        return 1

    def ambush_d(self):
        if not("Ambush" in self.skills_d):
            return 0
        if (self.d.ability["HP"]>int(self.d.ability["MHP"]/2)):
            return 0
        if (self.bspd_d*1.5<self.bspd_a):
            return 0
        return 1

    def charge_a(self):
        if (self.charged_combat==1):
            return 0
        if not("Charge" in self.skills_a):
            return 0
        if (self.bspd_a<=self.bspd_d):
            return 0
        return 1

    def charge_d(self):
        if (self.charged_combat==1):
            return 0
        if not("Charge" in self.skills_d):
            return 0
        if (self.bspd_d<=self.bspd_a):
            return 0
        return 1

    def continue_a(self,ca):
        if (ca==1):
            return 0
        if not("Continue" in self.skills_a):
            return 0
        p=self.a.ability["SPD"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def continue_d(self,ca):
        if (ca==1):
            return 0
        if not("Continue" in self.skills_d):
            return 0
        p=self.d.ability["SPD"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def weapon_duplicate_a(self,wd):
        if (wd==1):
            return 0
        if not("Weaponduplicate" in self.skills_a):
            return 0
        return 1

    def weapon_duplicate_d(self,wd):
        if (wd==1):
            return 0
        if not("Weaponduplicate" in self.skills_d):
            return 0
        return 1

    def shootingstar_a(self,sh):
        if (sh==1):
            return 0
        if not("Shootingstar" in self.skills_a):
            return 0
        p=self.a.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def shootingstar_d(self,sh):
        if (sh==1):
            return 0
        if not("Shootingstar" in self.skills_d):
            return 0
        p=self.d.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def skylight_a(self,se):
        if (se==1):
            return 0
        if not("Skylight" in self.skills_a):
            return 0
        p=int(float(self.a.ability["SKL"])*0.8)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def skylight_d(self,se):
        if (se==1):
            return 0
        if not("Skylight" in self.skills_d):
            return 0
        p=int(float(self.d.ability["SKL"])*0.8)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def eclipse_a(self,se):
        if (se==1):
            return 0
        if not("Eclipse" in self.skills_a):
            return 0
        p=int(float(self.a.ability["SKL"])*0.8)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def eclipse_d(self,se):
        if (se==1):
            return 0
        if not("Eclipse" in self.skills_d):
            return 0
        p=int(float(self.d.ability["SKL"])*0.8)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def moonlight_a(self):
        if not("Moonlight" in self.skills_a):
            return 0
        p=self.a.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def moonlight_d(self):
        if not("Moonlight" in self.skills_d):
            return 0
        p=self.d.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def wrath_a(self):
        if not("Wrath" in self.skills_a):
            return 0
        if (self.a.ability["HP"]>(self.a.ability["MHP"]/2)):
            return 0
        return 1

    def wrath_d(self):
        if not("Wrath" in self.skills_d):
            return 0
        if (self.d.ability["HP"]>(self.d.ability["MHP"]/2)):
            return 0
        return 1

    def sunlight_a(self):
        if not("Sunlight" in self.skills_a):
            return 0
        p=self.a.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def sunlight_d(self):
        if not("Sunlight" in self.skills_d):
            return 0
        p=self.d.ability["SKL"]
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def shield_a(self):
        if not("Shield" in self.skills_a):
            return 0
        p=self.a.ability["LV"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def shield_d(self):
        if not("Shield" in self.skills_d):
            return 0
        p=self.d.ability["LV"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def prayer_a(self):
        if not("Prayer" in self.skills_a):
            return 0
        p=self.a.ability["LUK"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def prayer_d(self):
        if not("Prayer" in self.skills_d):
            return 0
        p=self.d.ability["LUK"]*2
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def bane_a(self):
        if not("Bane" in self.skills_a):
            return 0
        if ("Resbane" in self.skills_d):
            return 0
        p=int(self.a.ability["SKL"]/2)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def bane_d(self):
        if not("Bane" in self.skills_d):
            return 0
        if ("Resbane" in self.skills_a):
            return 0
        p=int(self.d.ability["SKL"]/2)
        q=random.randint(0,99)
        if (q>=p):
            return 0
        return 1

    def battlea(self):
        self.queue.append(Attack(0,0,0,0,0,0))
        self.queue.append(Attack(1,0,0,0,0,0))
        if (self.ambush_d()==1):
            self.queue.pop()
            self.queue.pop()
            self.queue.append(Attack(1,0,0,0,0,0))
            self.queue.append(Attack(0,0,0,0,0,0))
            self.log.append((-2,"Ambush"))
        if (self.ambush_a()==1):
            self.queue.pop()
            self.queue.pop()
            self.queue.append(Attack(0,0,0,0,0,0))
            self.queue.append(Attack(1,0,0,0,0,0))
            self.log.append((-1,"Ambush"))
        if (self.bspd_a-self.bspd_d>=4):
            self.queue.append(Attack(0,0,0,0,0,0))
            self.log.append((-1,"Pursue"))
        if (self.bspd_d-self.bspd_a>=4):
            self.queue.append(Attack(1,0,0,0,0,0))
            self.log.append((-2,"Pursue"))
        while (True):
            if len(self.queue)==0:
                if (self.charge_a()==1):
                    self.charged_combat=1
                    self.queue.append(Attack(0,0,0,0,0,0))
                    self.queue.append(Attack(1,0,0,0,0,0))
                    self.log.append((-1,"Charge"))
                    if (self.bspd_a-self.bspd_d>=4):
                        self.queue.append(Attack(0,0,0,0,0,0))
                        self.log.append((-1, "Pursue"))
                    if (self.bspd_d-self.bspd_a>=4):
                        self.queue.append(Attack(1,0,0,0,0,0))
                        self.log.append((-2, "Pursue"))
                elif (self.charge_d()==1):
                    self.charged_combat=1
                    self.queue.append(Attack(0,0,0,0,0,0))
                    self.queue.append(Attack(1,0,0,0,0,0))
                    self.log.append((-1,"Charge"))
                    if (self.bspd_a-self.bspd_d>=4):
                        self.queue.append(Attack(0,0,0,0,0,0))
                        self.log.append((-1, "Pursue"))
                    if (self.bspd_d-self.bspd_a>=4):
                        self.queue.append(Attack(1,0,0,0,0,0))
                        self.log.append((-2, "Pursue"))
                else:
                    break
            att=self.queue.popleft()       #type:Attack
            r=self.execute(att)
            if (r==0):
                if att.AorD==0:
                    self.log.append((-1,"Brokenweapon"))
                else:
                    self.log.append((-2,"Brokenweapon"))
            if (r==2):
                if att.AorD==0:
                    self.log.append((-1,"Defeatenemy"))
                    return 1   #D defeated
                else:
                    self.log.append((-2,"Defeatenemy"))
                    return 2   #A defeated
        return 0

    def battleb(self):
        self.queue.append(Attack(0, 0, 0, 0, 0, 0))
        if (self.bspd_a - self.bspd_d >= 4):
            self.queue.append(Attack(0, 0, 0, 0, 0, 0))
            self.log.append((-1, "Pursue"))
        while (True):
            if len(self.queue) == 0:
                if (self.charge_a() == 1):
                    self.charged_combat = 1
                    self.queue.append(Attack(0, 0, 0, 0, 0, 0))
                    self.log.append((-1, "Charge"))
                    if (self.bspd_a - self.bspd_d >= 4):
                        self.queue.append(Attack(0, 0, 0, 0, 0, 0))
                        self.log.append((-1, "Pursue"))
                elif (self.charge_d() == 1):
                    self.charged_combat = 1
                    self.queue.append(Attack(0, 0, 0, 0, 0, 0))
                    self.log.append((-1, "Charge"))
                    if (self.bspd_a - self.bspd_d >= 4):
                        self.queue.append(Attack(0, 0, 0, 0, 0, 0))
                        self.log.append((-1, "Pursue"))
                else:
                    break
            att = self.queue.popleft()  # type:Attack
            r = self.execute(att)
            if (r == 0):
                if att.AorD == 0:
                    self.log.append((-1, "Brokenweapon"))
                else:
                    self.log.append((-2, "Brokenweapon"))
            if (r == 2):
                if att.AorD == 0:
                    self.log.append((-1, "Defeatenemy"))
                    return 1  # D defeated
                else:
                    self.log.append((-2, "Defeatenemy"))
                    return 2  # A defeated
        return 0

    def execute(self,_a):
        if (_a.AorD==0):
            return self.executea(_a)
        else:
            return self.executed(_a)

    def executea(self,_a):
        att=_a       #type:Attack
        if (self.wear_buf_a==0):
            return 0   #run out of weapon
        if (self.continue_a(att.continued_attack)==1):
            self.queue.append(Attack(0,1,0,0,0,0))
            self.log.append((-1,"Continue"))
        if (self.weapon_duplicate_a(att.wea_dup_attack)==1):
            self.queue.appendleft(Attack(0,att.continued_attack,1,0,0,0))
            self.log.appendleft((-1,"Weaponduplicate"))
        if (self.shootingstar_a(att.shootingstar_attack)==1):
            self.queue.appendleft(Attack(0,att.continued_attack,att.wea_dup_attack,1,0,0))
            self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.log.append((-1,"Shootingstar"))
        if (self.skylight_a(att.sky_ecl_attack)==1):
            self.att_sun=1
            self.queue.appendleft(Attack(0,att.continued_attack,att.wea_dup_attack,1,1,1))
            self.log.append((-1,"Skylight"))
        else:
            if (self.eclipse_a(att.sky_ecl_attack)==1):
                self.att_sun=1
                self.queue.appendleft(Attack(0,att.continued_attack,att.wea_dup_attack,1,1,0))
                self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(0, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.log.append((-1,"Eclipse"))
        if (att.moonlight_attack==1):
            self.att_moon=1
        elif (self.moonlight_a()==1):
            self.log.append((-1,"Moonlight"))
            self.att_moon=1
        if (self.wrath_a()==1):
            self.log.append((-1,"Wrath"))
            self.att_wrath=1
        self.calc_param()
        if (self.att_wrath==1):
            self.crta=int(float(self.crta)*1.5)
        crtb=self.crta-self.crad
        q=random.randint(0,99)
        if (q<crtb):
            self.att_crt=1
        if (self.sunlight_a()==1):
            self.att_sun=1
            self.log.append((-1,"Sunlight"))
        hitb=self.hita-self.avod
        if (self.bane_a()==1):
            self.atka+=65536
            self.log.append((-1,"Bane"))
        if (self.shield_d()==1):
            self.att_shield=1
            self.log.append((-2,"Shield"))
        dmg=(self.atka-self.defd)*(1-self.att_shield)*(1+2*self.att_crt)*self.combo_bonusa
        self.combo_bonusa = self.combo_bonusa * (1 + self.redseala)
        if (dmg<0):
            dmg=0
        if (dmg>self.d.ability["HP"]):
            dmg=self.d.ability["HP"]
        if (dmg==self.d.ability["HP"]):
            if (self.prayer_d()==1):
                hitb=0
                self.log.append((-2,"Prayer"))
            elif (self.immortald==1):
                hitb=0
                self.log.append((-2,"Immortal"))
        q=random.randint(0,99)
        if (q<hitb):
            s=""
            if (self.att_crt==1):
                s+="C,"     #critical
            elif (dmg==0):
                s+="N,"     #no damage
            else:
                s+="H,"     #normal hit
            s+=str(dmg)
            s+=","
            hpadd=0
            if (self.att_sun==1):
                hpadd=dmg
                if (hpadd>self.a.ability["MHP"]-self.a.ability["HP"]):
                    hpadd=self.a.ability["MHP"]-self.a.ability["HP"]
            s+=str(hpadd)
            self.log.append((1,s))
            self.weapon_rank_buf_a+=1
            self.wear_buf_a-=1
            self.exp_buf_a+=1
            self.exp_buf_d+=1
            self.att_sun=0
            self.att_moon=0
            self.att_wrath=0
            self.att_crt=0
            self.att_shield=0
            self.d.ability["HP"]-=dmg
            if (self.d.ability["HP"]<=0):
                return 2
            return 1
        else:
            self.weapon_rank_buf_a+=1
            self.exp_buf_a+=1
            self.exp_buf_d+=1
            self.att_sun=0
            self.att_moon=0
            self.att_wrath = 0
            self.att_crt = 0
            self.att_shield = 0
            self.log.append((1,"M,0,0")) #miss
            return 3
        return 0


    def executed(self,_a):
        att=_a       #type:Attack
        if (self.wear_buf_d==0):
            return 0   #run out of weapon
        if (self.continue_d(att.continued_attack)==1):
            self.queue.append(Attack(1,1,0,0,0,0))
            self.log.appendleft((-2,"Continue"))
        if (self.weapon_duplicate_d(att.wea_dup_attack)==1):
            self.queue.append(Attack(1,att.continued_attack,1,0,0,0))
            self.log.appendleft((-2,"Weaponduplicate"))
        if (self.shootingstar_d(att.shootingstar_attack)==1):
            self.queue.appendleft(Attack(1,att.continued_attack,att.wea_dup_attack,1,0,0))
            self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 0, 0))
            self.log.append((-2,"Shootingstar"))
        if (self.skylight_d(att.sky_ecl_attack)==1):
            self.att_sun=1
            self.queue.appendleft(Attack(1,att.continued_attack,att.wea_dup_attack,1,1,1))
            self.log.append((-2,"Skylight"))
        else:
            if (self.eclipse_d(att.sky_ecl_attack)==1):
                self.att_sun=1
                self.queue.appendleft(Attack(1,att.continued_attack,att.wea_dup_attack,1,1,0))
                self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.queue.appendleft(Attack(1, att.continued_attack, att.wea_dup_attack, 1, 1, 0))
                self.log.append((-2,"Eclipse"))
        if (att.moonlight_attack==1):
            self.att_moon=1
        elif (self.moonlight_d()==1):
            self.log.append((-2,"Moonlight"))
            self.att_moon=1
        if (self.wrath_d()==1):
            self.log.append((-2,"Wrath"))
            self.att_wrath=1
        self.calc_param()
        if (self.att_wrath==1):
            self.crtd=int(float(self.crtd)*1.5)
        crtb=self.crtd-self.craa
        q=random.randint(0,99)
        if (q<crtb):
            self.att_crt=1
        if (self.sunlight_d()==1):
            self.att_sun=1
            self.log.append((-2,"Sunlight"))
        hitb=self.hitd-self.avoa
        if (self.bane_d()==1):
            self.atkd+=65536
            self.log.append((-2,"Bane"))
        if (self.shield_a()==1):
            self.att_shield=1
            self.log.append((-1,"Shield"))
        dmg=(self.atkd-self.defa)*(1-self.att_shield)*(1+2*self.att_crt)*self.combo_bonusd
        self.combo_bonusd = self.combo_bonusd * (1 + self.redseald)
        if (dmg<0):
            dmg=0
        if (dmg>self.a.ability["HP"]):
            dmg=self.a.ability["HP"]
        if (dmg==self.a.ability["HP"]):
            if (self.prayer_a()==1):
                hitb=0
                self.log.append((-1,"Prayer"))
            elif (self.immortala==1):
                hitb=0
                self.log.append((-1,"Immortal"))
        q=random.randint(0,99)
        if (q<hitb):
            s=""
            if (self.att_crt==1):
                s+="C,"     #critical
            elif (dmg==0):
                s+="N,"     #no damage
            else:
                s+="H,"     #normal hit
            s+=str(dmg)
            s+=","
            hpadd=0
            if (self.att_sun==1):
                hpadd=dmg
                if (hpadd>self.d.ability["MHP"]-self.d.ability["HP"]):
                    hpadd=self.d.ability["MHP"]-self.d.ability["HP"]
            s+=str(hpadd)
            self.log.append((2,s))
            self.weapon_rank_buf_d+=1
            self.wear_buf_d-=1
            self.exp_buf_d+=1
            self.exp_buf_a+=1
            self.att_sun=0
            self.att_moon=0
            self.att_wrath=0
            self.att_crt=0
            self.att_shield=0
            self.a.ability["HP"]-=dmg
            if (self.a.ability["HP"]<=0):
                return 2
            return 1
        else:
            self.weapon_rank_buf_d += 1
            self.exp_buf_d += 1
            self.exp_buf_a += 1
            self.att_sun = 0
            self.att_moon = 0
            self.att_wrath = 0
            self.att_crt = 0
            self.att_shield = 0
            self.log.append((2,"M,0,0"))
            return 3
        return 0








