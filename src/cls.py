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
        pass
    def __init__(self,data):
        self.cls_bank=ClsBank(data.cls_typenames,data.cls_weapon_rank,data.cls_clsgroup,data.cls_skills,data.cls_ability_limit).cls_bank