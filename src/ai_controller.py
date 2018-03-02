from typing import List,Tuple
import random
import map_controller
from utility import *
from battle import Battle
class AI_Controller:
    def __init__(self):
        pass
    def enemy_single_movement(self,_valid,_invalid,_ally,_enemy,mapcontroller):
        valid=_valid   #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        invalid=_invalid #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        ally=_ally    #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        enemy=_enemy   #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        map=mapcontroller #type:map_controller.Main
        if len(valid)==0:
            return ["E",]
        ring=65536
        candidates=[]   #type:List[str]
        for p in valid:
            if map.person_container.AItype[p][0]<ring:
                ring=map.person_container.AItype[p][0]
                candidates.clear()
                candidates.append(p)
            elif map.person_container.AItype[p][0]==ring:
                candidates.append(p)
        person_to_move=random.choice(candidates)
        return self.individual_movement(valid,invalid,ally,enemy,map,person_to_move)

    def choose_attack_obj(self,attack_candidate):
        obj=None
        for candidate in attack_candidate:
            if candidate[3][5]*(1+candidate[3][2])>=candidate[1].ability["HP"]:
                if obj is None:
                    obj=candidate
                else:
                    if candidate[3][3]>=obj[3][3]:
                        obj=candidate
        if obj is None:
            for candidate in attack_candidate:
                if candidate[3][0]==1:
                    if obj is None:
                        obj=candidate
                    else:
                        if candidate[3][5]*(1+candidate[3][2])>=obj[3][5]*(1+obj[3][2]):
                            obj=candidate
        if obj is None:
            minhp=999
            for candidate in attack_candidate:
                if candidate[1].ability["HP"]-candidate[3][5]*(1+candidate[3][2])<minhp:
                    minhp=candidate[1].ability["HP"]-candidate[3][5]*(1+candidate[3][2])
                    obj=candidate
        if obj is None:
            obj=random.choice(attack_candidate)
        return obj

    def individual_movement(self,_valid,_invalid,_ally,_enemy,_map,_person_to_move):
        p=_person_to_move
        strategy=_map.person_container.AItype[p][1]
        person=_map.global_vars.personBank[p]
        pos = _map.person_container.position[p]
        if strategy=="STAY":
            return ["M",person,pos,[pos]]
        if strategy=="DEFENSIVE":
            attack_candidate=[]
            if len(person.item)>0:
                for weap in person.item:
                    if _map.attackable(weap.itemtype.weapontype):
                        minrange=weap.itemtype.min_range
                        maxrange=weap.itemtype.max_range
                        for enm in _enemy:
                            pose=_map.person_container.position[enm]
                            if (calc_dist(pose,pos)>=minrange)and(calc_dist(pose,pos)<=maxrange):
                                enemy_person=_map.global_vars.personBank[enm]
                                bat=Battle(person,enemy_person,weap,enemy_person.get_equip(),_map,pos)
                                sim=bat.simulate()
                                del(bat)
                                attack_candidate.append((pos,enemy_person,weap,sim))
            if len(attack_candidate)>0:
                attack_object=self.choose_attack_obj(attack_candidate)
                return ["A",person,pos,[pos],attack_object[1],attack_object[2]]
            else:
                return ["M",person,pos,[pos]]
        if strategy=="PASSIVE":
            movement_candidate=[]
            dst_to_move_list=_valid[p]
            for dst in dst_to_move_list:
                if len(person.item) > 0:
                    for weap in person.item:
                        if _map.can_equip(p,weap):#attackable(weap.itemtype.weapontype):
                            minrange = weap.itemtype.min_range
                            maxrange = weap.itemtype.max_range
                            for enm in _enemy:
                                pose = _map.person_container.position[enm]
                                if (calc_dist(pose, dst) >= minrange) and (calc_dist(pose, dst) <= maxrange):
                                    enemy_person = _map.global_vars.personBank[enm]
                                    bat = Battle(person, enemy_person, weap, enemy_person.get_equip(), _map, dst)
                                    sim = bat.simulate()
                                    del(bat)
                                    movement_candidate.append((dst,enemy_person, weap, sim))
            if len(movement_candidate)>0:
                attack_object=self.choose_attack_obj(movement_candidate)
                dst=attack_object[0]
                track=dst_to_move_list[dst][1]
                return ["A",person,dst,track,attack_object[1],attack_object[2]]
            else:
                return ["M",person,pos,[pos]]
        if strategy=="NULL":
            dst_to_move_list=_valid[p]
            dst_to_move=random.choice(list(dst_to_move_list.keys()))
            track=dst_to_move_list[dst_to_move][1]
            return ["M",person,dst_to_move,track]
        return ["E"]