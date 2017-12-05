class Cls:
    def __init__(self):
        pass
    def __init__(self,name,weapon_rank,group,skills,ability_limit):
        self.name=name                                             #"Lord"
        self.weapon_rank=weapon_rank                               #{"Sword":1,"Lance":-65536",}
        self.cls_group=group                                       #"Infantry"
        self.cls_skills=skills                                     #list(["Prayer","Shootingstar",])
        self.ability_limit=ability_limit                           #{"MHP":60,"STR":20,"MGC":5,}

class ClsBank:
    def __init__(self):
        pass
    def __init__(self,typenamelist,weapon_ranks,cls_group,skills,ability_limit):
        self.cls_bank={}
        for name in typenamelist:
            cls=Cls(name,weapon_ranks[name],cls_group[name],skills[name],ability_limit[name])
            self.cls_bank[name]=cls

class Main:
    def __init__(self):
        typenamelist=list(["Lord","Cavalier"])
        weapon_ranks={}
        weapon_ranks["Lord"]={"Sword":1,"Lance":-65536,"Axe":-65536,"Bow":-65536,
                              "Fire":-65536,"Thunder":-65536,"Wind":-65536,
                              "Light":-65536,"Dark":-65536,"Wand":-65536}
        weapon_ranks["Cavalier"]={"Sword":1,"Lance":1,"Axe":-65536,"Bow":-65536,
                              "Fire":-65536,"Thunder":-65536,"Wind":-65536,
                              "Light":-65536,"Dark":-65536,"Wand":-65536}
        cls_group={"Lord":"Infantry","Cavalier":"Knight"}
        skills={"Lord":list([]),"Cavalier":list([])}
        ability_limit={}
        ability_limit["Lord"]={"LV":20,"MHP":60,"STR":20,"MGC":10,"SPD":20,"SKL":20,
                               "DEF":20,"RES":20,"LUK":50,"BLD":20,"MOV":20,"HP":120,"CRY":20}
        ability_limit["Cavalier"] = {"LV": 20, "MHP": 60, "STR": 20, "MGC": 5, "SPD": 20, "SKL": 20,
                                 "DEF": 20, "RES": 20, "LUK": 50, "BLD": 20, "MOV": 20, "HP": 120, "CRY": 20}
        self.cls_bank=ClsBank(typenamelist,weapon_ranks,cls_group,skills,ability_limit).cls_bank
    def __init__(self,data):
        self.cls_bank=ClsBank(data.cls_typenames,data.cls_weapon_rank,data.cls_clsgroup,data.cls_skills,data.cls_ability_limit).cls_bank