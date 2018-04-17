from typing import List,Tuple
import random
import map_controller
from utility import *
import battle
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

    def choose_attack_obj(self,strategy,attack_candidate):
        obj=None
        for ao in strategy["Attack_Selection"]:
            if ao=="Fatal":
                for candidate in attack_candidate:
                    if candidate[1].pid in strategy["Not_Attack"]:
                        continue
                    if candidate[3][5]*(1+candidate[3][2])>=candidate[1].ability["HP"]:
                        if candidate[3][3]>0:
                            if obj is None:
                                obj=candidate
                            else:
                                if candidate[3][3]>=obj[3][3]:
                                    obj=candidate
                if not (obj==None):
                    break
            if ao=="Object":
                rank=9999
                for candidate in attack_candidate:
                    if candidate[1].pid in strategy["Not_Attack"]:
                        continue
                    if candidate[1].pid in strategy["Attack_Obj"]:
                        if (candidate[3][5]>0)and(candidate[3][3]>0):
                            if strategy["Attack_Obj"].index(candidate[1].pid)<rank:
                                rank=strategy["Attack_Obj"].index(candidate[1].pid)
                                obj=candidate
                            elif strategy["Attack_Obj"].index(candidate[1].pid)==rank:
                                if candidate[3][0]==1:
                                    obj=candidate
                if not(obj==None):
                    break
            if ao=="Uncountered":
                for candidate in attack_candidate:
                    if candidate[1].pid in strategy["Not_Attack"]:
                        continue
                    if candidate[3][0]==1:
                        if candidate[3][3]>0 and candidate[3][5]>0:
                            if obj is None:
                                obj=candidate
                            else:
                                if candidate[3][5]*(1+candidate[3][2])>=obj[3][5]*(1+obj[3][2]):
                                    obj=candidate
                if not(obj==None):
                    break
            if ao=="Any":
                minhp=9999
                for candidate in attack_candidate:
                    if candidate[1].pid in strategy["Not_Attack"]:
                        continue
                    if candidate[1].ability["HP"]-candidate[3][5]*(1+candidate[3][2])<minhp:
                        if candidate[3][3]>0 and candidate[3][5]>0:
                            minhp=candidate[1].ability["HP"]-candidate[3][5]*(1+candidate[3][2])
                            obj=candidate
                if obj is None:
                    obj=random.choice(attack_candidate)
                if obj[1].pid in strategy["Not_Attack"]:
                    return None
        return obj

    def find_geographical_shortest(self,p,_map,tarpos):
        wait = {}
        dst = {}
        pos = tarpos#_map.person_container.position[p.pid]
        wait[pos] = float(0)
        M = _map.terrain_container.M
        N = _map.terrain_container.N
        while not len(dst)==M*N:
            (tpos, r) = min(wait.items(), key=lambda x: x[1])
            dst[tpos] = r
            wait.pop(tpos)
            if tpos[0] > 0:
                npos = (tpos[0] - 1, tpos[1])
                if not (npos in dst):
                    tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[
                        _map.global_vars.data.cls_clsgroup[p.cls]]
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[0] < M - 1:
                npos = (tpos[0] + 1, tpos[1])
                if not (npos in dst):
                    tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[
                        _map.global_vars.data.cls_clsgroup[p.cls]]
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                                wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[1] > 0:
                npos = (tpos[0], tpos[1] - 1)
                if not (npos in dst):
                    tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[
                        _map.global_vars.data.cls_clsgroup[p.cls]]
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[1] < N - 1:
                npos = (tpos[0], tpos[1] + 1)
                if not (npos in dst):
                    tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[
                        _map.global_vars.data.cls_clsgroup[p.cls]]
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
        return dst

    def find_relative_shortest(self,p,_map,tarpos):
        wait = {}
        dst = {}
        pos = tarpos#_map.person_container.position[p.pid]
        wait[pos] = float(0)
        M = _map.terrain_container.M
        N = _map.terrain_container.N
        while not len(dst)==M*N:
            (tpos, r) = min(wait.items(), key=lambda x: x[1])
            dst[tpos] = r
            wait.pop(tpos)
            if tpos[0] > 0:
                npos = (tpos[0] - 1, tpos[1])
                if not (npos in dst):
                    occ=0
                    for _p in _map.person_container.position:
                        if not (_map.person_container.controller[_p]%2==_map.person_container.controller[p.pid]%2):
                            if _map.person_container.position[_p] == tpos:
                                occ = 1
                                break
                    if occ==0:
                        tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[_map.global_vars.data.cls_clsgroup[p.cls]]
                    else:
                        tr=r+255
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[0] < M - 1:
                npos = (tpos[0] + 1, tpos[1])
                if not (npos in dst):
                    occ=0
                    for _p in _map.person_container.position:
                        if not (_map.person_container.controller[_p]%2==_map.person_container.controller[p.pid]%2):
                            if _map.person_container.position[_p] == tpos:
                                occ = 1
                                break
                    if occ==0:
                        tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[_map.global_vars.data.cls_clsgroup[p.cls]]
                    else:
                        tr=r+255
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[1] > 0:
                npos = (tpos[0], tpos[1] - 1)
                if not (npos in dst):
                    occ=0
                    for _p in _map.person_container.position:
                        if not (_map.person_container.controller[_p]%2==_map.person_container.controller[p.pid]%2):
                            if _map.person_container.position[_p] == tpos:
                                occ = 1
                                break
                    if occ==0:
                        tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[_map.global_vars.data.cls_clsgroup[p.cls]]
                    else:
                        tr=r+255
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
            if tpos[1] < N - 1:
                npos = (tpos[0], tpos[1] + 1)
                if not (npos in dst):
                    occ=0
                    for _p in _map.person_container.position:
                        if not (_map.person_container.controller[_p]%2==_map.person_container.controller[p.pid]%2):
                            if _map.person_container.position[_p] == tpos:
                                occ = 1
                                break
                    if occ==0:
                        tr = r + _map.terrain_container.map[tpos[0]][tpos[1]].decay[_map.global_vars.data.cls_clsgroup[p.cls]]
                    else:
                        tr=r+255
                    if npos in wait:
                        r0 = wait[npos]
                        if tr < r0:
                            wait[npos] = tr
                    else:
                        wait[npos] = tr
        return dst

    def find_push_action(self,p,_map,tar,valid):
        tarpos=_map.person_container.position[tar]
        dst=self.find_geographical_shortest(p,_map,tarpos)
        pos=_map.person_container.position[p.pid]
        if dst[pos]>100:
            return (None,None)
        while True:
            (tpos, r) = min(dst.items(), key=lambda x: x[1])
            dst.pop(tpos)
            if tpos in valid[p.pid]:
                return (tpos,valid[p.pid][tpos][1]) #moveto,track

    def individual_movement(self,_valid,_invalid,_ally,_enemy,_map,_person_to_move):
        p=_person_to_move
        strategy=_map.person_container.AItype[p][1]
        person=_map.global_vars.personBank[p]
        pos = _map.person_container.position[p]
        if strategy["Strategy"]=="PURSUE":
            for tar in strategy["Push"]:
                tartp = tar.split(",")
                if len(tartp) == 1:
                    push_pid = tartp[0]
                    if push_pid in _map.person_container.position:
                        (move_to, track) = self.find_push_action(person, _map, push_pid,_valid)
                        if not move_to == None:
                            attack_candidate = []
                            if len(person.item) > 0:
                                for weap in person.item:
                                    if _map.can_equip(p,weap):
                                        minrange = weap.itemtype.min_range
                                        maxrange = weap.itemtype.max_range
                                        for enm in _enemy:
                                            pose = _map.person_container.position[enm]
                                            if (calc_dist(pose, move_to) >= minrange) and (
                                                calc_dist(pose, move_to) <= maxrange):
                                                enemy_person = _map.global_vars.personBank[enm]
                                                bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map,
                                                             move_to)
                                                sim = bat.simulate()
                                                del (bat)
                                                attack_candidate.append((move_to, enemy_person, weap, sim))
                            if len(attack_candidate) > 0:
                                attack_object = self.choose_attack_obj(strategy, attack_candidate)
                                if not (attack_object == None):
                                    return ["A",person,move_to,track,attack_object[1],attack_object[2]]
                            return ["M", person, move_to, track]
                else:
                    tarpos = (int(tartp[0]), int(tartp[1]))
                    dst_g = self.find_geographical_shortest(person, _map, tarpos)
                    dst_r = self.find_relative_shortest(person, _map, tarpos)
                    # print(tarpos,rem_mov_g,rem_mov_r)
                    if (dst_r[pos] - dst_g[pos] <= person.ability["MOV"]) and (dst_r[pos] <= 100):
                        while True:
                            (moveto_r, rem_mov_r) = min(dst_r.items(), key=lambda x: x[1])
                            dst_r.pop(moveto_r)
                            if moveto_r in _valid[person.pid]:
                                track_r = _valid[person.pid][moveto_r][1]
                                break
                        attack_candidate = []
                        if len(person.item) > 0:
                            for weap in person.item:
                                if _map.can_equip(p, weap):
                                    minrange = weap.itemtype.min_range
                                    maxrange = weap.itemtype.max_range
                                    for enm in _enemy:
                                        pose = _map.person_container.position[enm]
                                        if (calc_dist(pose, moveto_r) >= minrange) and (
                                                    calc_dist(pose, moveto_r) <= maxrange):
                                            enemy_person = _map.global_vars.personBank[enm]
                                            bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map,
                                                         moveto_r)
                                            sim = bat.simulate()
                                            del (bat)
                                            attack_candidate.append((moveto_r, enemy_person, weap, sim))
                        if len(attack_candidate) > 0:
                            attack_object = self.choose_attack_obj(strategy, attack_candidate)
                            if not (attack_object == None):
                                return ["A", person, moveto_r, track_r, attack_object[1], attack_object[2]]
                        return ["M", person, moveto_r, track_r]
                        # find way on relative best route
                    else:
                        attack_tars=_map.get_attack_target(person.pid,_valid)
                        while True:
                            (moveto_g, rem_mov_g) = min(dst_g.items(), key=lambda x:x[1])
                            dst_g.pop(moveto_g)
                            for _p in _map.person_container.position:
                                if _p in attack_tars:
                                    minr=1000
                                    minppos=attack_tars[_p][0]
                                    for ppos in attack_tars[_p]:
                                        if ppos in dst_g:
                                            if dst_g[ppos]<minr:
                                                minr=dst_g[ppos]
                                                minppos=ppos
                                    moveto_g=minppos
                                    track_g=_valid[person.pid][moveto_g][1]
                                    movement_candidate=[]
                                    if len(person.item) > 0:
                                        for weap in person.item:
                                            if _map.can_equip(p,weap):  # attackable(weap.itemtype.weapontype):
                                                minrange = weap.itemtype.min_range
                                                maxrange = weap.itemtype.max_range
                                                enm=_p
                                                pose = _map.person_container.position[enm]
                                                if (calc_dist(pose, moveto_g) >= minrange) and (calc_dist(pose, moveto_g) <= maxrange):
                                                        enemy_person = _map.global_vars.personBank[enm]
                                                        bat = battle.Battle(person, enemy_person, weap,
                                                                     enemy_person.get_equip(), _map, moveto_g)
                                                        sim = bat.simulate()
                                                        del (bat)
                                                        movement_candidate.append(
                                                            (moveto_g, enemy_person, weap, sim))
                                    if len(movement_candidate) > 0:
                                        attack_object = self.choose_attack_obj(strategy, movement_candidate)
                                        return ["A", person, moveto_g, track_g, attack_object[1], attack_object[2]]
                            if moveto_g in _valid[person.pid]:
                                track_g=_valid[person.pid][moveto_g][1]
                                break
                        attack_candidate = []
                        if len(person.item) > 0:
                            for weap in person.item:
                                if _map.can_equip(p, weap):
                                    minrange = weap.itemtype.min_range
                                    maxrange = weap.itemtype.max_range
                                    for enm in _enemy:
                                        pose = _map.person_container.position[enm]
                                        if (calc_dist(pose, moveto_g) >= minrange) and (
                                                    calc_dist(pose, moveto_g) <= maxrange):
                                            enemy_person = _map.global_vars.personBank[enm]
                                            bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map,
                                                         moveto_g)
                                            sim = bat.simulate()
                                            del (bat)
                                            attack_candidate.append((moveto_g, enemy_person, weap, sim))
                        if len(attack_candidate) > 0:
                            attack_object = self.choose_attack_obj(strategy, attack_candidate)
                            if not (attack_object == None):
                                return ["A", person, moveto_g, track_g, attack_object[1], attack_object[2]]
                        return ["M", person, moveto_g, track_g]
            return ["M", person, pos, [pos]]
        if strategy["Strategy"]=="ACTIVE":
            movement_candidate = []
            dst_to_move_list = _valid[p]
            for dst in dst_to_move_list:
                if len(person.item) > 0:
                    for weap in person.item:
                        if _map.can_equip(p, weap):  # attackable(weap.itemtype.weapontype):
                            minrange = weap.itemtype.min_range
                            maxrange = weap.itemtype.max_range
                            for enm in _enemy:
                                pose = _map.person_container.position[enm]
                                if (calc_dist(pose, dst) >= minrange) and (calc_dist(pose, dst) <= maxrange):
                                    enemy_person = _map.global_vars.personBank[enm]
                                    bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map, dst)
                                    sim = bat.simulate()
                                    del (bat)
                                    movement_candidate.append((dst, enemy_person, weap, sim))
            if len(movement_candidate) > 0:
                attack_object = self.choose_attack_obj(strategy, movement_candidate)
                if not (attack_object == None):
                    dst = attack_object[0]
                    track = dst_to_move_list[dst][1]
                    return ["A", person, dst, track, attack_object[1], attack_object[2]]
            for tar in strategy["Push"]:
                tartp=tar.split(",")
                if len(tartp)==1:
                    push_pid=tartp[0]
                    if push_pid in _map.person_container.position:
                        (move_to,track)=self.find_push_action(person,_map,push_pid,_valid)
                        if not move_to==None:
                            return ["M",person,move_to,track]
                else:
                    tarpos=(int(tartp[0]),int(tartp[1]))
                    dst_g=self.find_geographical_shortest(person,_map,tarpos)
                    dst_r=self.find_relative_shortest(person,_map,tarpos)
                    #print(tarpos,rem_mov_g,rem_mov_r)
                    if (dst_r[pos] - dst_g[pos] <= person.ability["MOV"]) and (dst_r[pos] <= 100):
                        while True:
                            (moveto_r, rem_mov_r) = min(dst_r.items(), key=lambda x: x[1])
                            dst_r.pop(moveto_r)
                            if moveto_r in _valid[person.pid]:
                                track_r = _valid[person.pid][moveto_r][1]
                                break
                        attack_candidate = []
                        if len(person.item) > 0:
                            for weap in person.item:
                                if _map.can_equip(p, weap):
                                    minrange = weap.itemtype.min_range
                                    maxrange = weap.itemtype.max_range
                                    for enm in _enemy:
                                        pose = _map.person_container.position[enm]
                                        if (calc_dist(pose, moveto_r) >= minrange) and (
                                                    calc_dist(pose, moveto_r) <= maxrange):
                                            enemy_person = _map.global_vars.personBank[enm]
                                            bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map,
                                                         moveto_r)
                                            sim = bat.simulate()
                                            del (bat)
                                            attack_candidate.append((moveto_r, enemy_person, weap, sim))
                        if len(attack_candidate) > 0:
                            attack_object = self.choose_attack_obj(strategy, attack_candidate)
                            if not (attack_object == None):
                                return ["A", person, moveto_r, track_r, attack_object[1], attack_object[2]]
                        return ["M", person, moveto_r, track_r]
                        # find way on relative best route
                    else:
                        attack_tars = _map.get_attack_target(person.pid, _valid)
                        while True:
                            (moveto_g, rem_mov_g) = min(dst_g.items(), key=lambda x: x[1])
                            dst_g.pop(moveto_g)
                            for _p in _map.person_container.position:
                                if _p in attack_tars:
                                    minr = 1000
                                    minppos = attack_tars[_p][0]
                                    for ppos in attack_tars[_p]:
                                        if ppos in dst_g:
                                            if dst_g[ppos] < minr:
                                                minr = dst_g[ppos]
                                                minppos = ppos
                                    moveto_g = minppos
                                    track_g = _valid[person.pid][moveto_g][1]
                                    movement_candidate = []
                                    if len(person.item) > 0:
                                        for weap in person.item:
                                            if _map.can_equip(p, weap):  # attackable(weap.itemtype.weapontype):
                                                minrange = weap.itemtype.min_range
                                                maxrange = weap.itemtype.max_range
                                                enm = _p
                                                pose = _map.person_container.position[enm]
                                                if (calc_dist(pose, moveto_g) >= minrange) and (
                                                    calc_dist(pose, moveto_g) <= maxrange):
                                                    enemy_person = _map.global_vars.personBank[enm]
                                                    bat = battle.Battle(person, enemy_person, weap,
                                                                 enemy_person.get_equip(), _map, moveto_g)
                                                    sim = bat.simulate()
                                                    del (bat)
                                                    movement_candidate.append(
                                                        (moveto_g, enemy_person, weap, sim))
                                    if len(movement_candidate) > 0:
                                        attack_object = self.choose_attack_obj(strategy, movement_candidate)
                                        return ["A", person, moveto_g, track_g, attack_object[1], attack_object[2]]
                            if moveto_g in _valid[person.pid]:
                                track_g = _valid[person.pid][moveto_g][1]
                                break
                        attack_candidate = []
                        if len(person.item) > 0:
                            for weap in person.item:
                                if _map.can_equip(p, weap):
                                    minrange = weap.itemtype.min_range
                                    maxrange = weap.itemtype.max_range
                                    for enm in _enemy:
                                        pose = _map.person_container.position[enm]
                                        if (calc_dist(pose, moveto_g) >= minrange) and (
                                                    calc_dist(pose, moveto_g) <= maxrange):
                                            enemy_person = _map.global_vars.personBank[enm]
                                            bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map,
                                                         moveto_g)
                                            sim = bat.simulate()
                                            del (bat)
                                            attack_candidate.append((moveto_g, enemy_person, weap, sim))
                        if len(attack_candidate) > 0:
                            attack_object = self.choose_attack_obj(strategy, attack_candidate)
                            if not (attack_object == None):
                                return ["A", person, moveto_g, track_g, attack_object[1], attack_object[2]]
                        return ["M", person, moveto_g, track_g]
            return ["M", person, pos, [pos]]
        if strategy["Strategy"]=="STAY":
            return ["M",person,pos,[pos]]
        if strategy["Strategy"]=="DEFENSIVE":
            attack_candidate=[]
            if len(person.item)>0:
                for weap in person.item:
                    if _map.can_equip(p,weap):
                        minrange=weap.itemtype.min_range
                        maxrange=weap.itemtype.max_range
                        for enm in _enemy:
                            pose=_map.person_container.position[enm]
                            if (calc_dist(pose,pos)>=minrange)and(calc_dist(pose,pos)<=maxrange):
                                enemy_person=_map.global_vars.personBank[enm]
                                bat=battle.Battle(person,enemy_person,weap,enemy_person.get_equip(),_map,pos)
                                sim=bat.simulate()
                                del(bat)
                                attack_candidate.append((pos,enemy_person,weap,sim))
            if len(attack_candidate)>0:
                attack_object=self.choose_attack_obj(strategy,attack_candidate)
                if not (attack_object==None):
                    return ["A",person,pos,[pos],attack_object[1],attack_object[2]]
                else:
                    return ["M",person,pos,[pos]]
            else:
                return ["M",person,pos,[pos]]
        if strategy["Strategy"]=="PASSIVE":
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
                                    bat = battle.Battle(person, enemy_person, weap, enemy_person.get_equip(), _map, dst)
                                    sim = bat.simulate()
                                    del(bat)
                                    movement_candidate.append((dst,enemy_person, weap, sim))
            if len(movement_candidate)>0:
                attack_object=self.choose_attack_obj(strategy,movement_candidate)
                if not (attack_object==None):
                    dst=attack_object[0]
                    track=dst_to_move_list[dst][1]
                    return ["A",person,dst,track,attack_object[1],attack_object[2]]
                else:
                    return ["M",person,pos,[pos]]
            else:
                return ["M",person,pos,[pos]]
        if strategy["Strategy"]=="NULL":
            dst_to_move_list=_valid[p]
            dst_to_move=random.choice(list(dst_to_move_list.keys()))
            track=dst_to_move_list[dst_to_move][1]
            return ["M",person,dst_to_move,track]
        return ["E"]