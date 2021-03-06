from typing import List,Dict,Tuple
from . import terrain_container
from . import person_container
from . import move_range_person
from . import global_vars
from . import person
from .utility import *

def execute(valid,invalid,ally,enemy):
    for item in valid:
        print(item,"Valid")
    for item in invalid:
        print(item,"Invalid")
    for item in ally:
        print(item,"Ally")
    for item in enemy:
        print(item,"Enemy")
class Main:
    def __init__(self):
        self.terrain_container=None     #type:terrain_container.Main
        self.person_container=None      #type:person_container.Main
        self.global_vars=None           #type:global_vars.Main
        self.turn=0
        self.controller=0
        self.eventlist={}
        self.pre=[]
        self.after=[]
        self.pic=""
        self.scene=""
        self.title=""
        self.reconstruct_log=[]
        self.leader="1"
        self.vic=""
    def __init__(self,terrain_map,person_container,glb,reconstruct_log=[],eventlist={},pre=[],after=[],pic="",scene="",title="",leader="1",victory=""):
        self.terrain_container=terrain_map
        self.person_container=person_container
        self.turn=0
        self.pre = pre
        self.after = after
        self.pic = pic
        self.scene = scene
        self.title = title
        self.controller=0
        self.global_vars=glb
        self.eventlist=eventlist
        self.reconstruct_log = reconstruct_log
        self.leader=leader
        self.vic=victory
        for p in self.person_container.people:
            p.status.clear()
            p.ability["HP"]=p.ability["MHP"]
            if (self.person_container.controller[p.pid]==0) and (p.pid in self.global_vars.player_character_status):
                if (self.global_vars.player_character_status[p.pid]==0)\
                        or(self.global_vars.player_character_status[p.pid]==2):
                    self.person_container.controller.pop(p.pid)
                    self.person_container.position.pop(p.pid)
                    self.person_container.movable.pop(p.pid)
                    self.person_container.army.pop(p.pid)
                    self.person_container.AItype.pop(p.pid)
    def unstable_valid_grid(self,pid):
        unstable=[]
        uncross=[]
        p=self.global_vars.personBank[pid]
        pos=self.person_container.position[p.pid]
        mov=p.ability["MOV"]
        for other in self.person_container.people:
            if not p is other:
                if self.person_container.controller[other.pid]%2 == self.person_container.controller[p.pid]%2:
                    unstable.append(self.person_container.position[other.pid])
                else:
                    uncross.append(self.person_container.position[other.pid])
        movmap={}
        for i in range(self.terrain_container.M):
            for j in range(self.terrain_container.N):
                movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
        unstablevalid = move_range_person.unstablevalid(unstable, uncross, movmap, pos, mov, self.terrain_container.M,
                                              self.terrain_container.N)
        return unstablevalid

    def move_and_attack_range(self,pid):
        uncross=[]
        p=self.global_vars.personBank[pid]
        pos=self.person_container.position[p.pid]
        mov=p.ability["MOV"]
        for other in self.person_container.people:
            if not p is other:
                if self.person_container.controller[other.pid]%2 == self.person_container.controller[p.pid]%2:
                    pass
                else:
                    uncross.append(self.person_container.position[other.pid])
        movmap={}
        for i in range(self.terrain_container.M):
            for j in range(self.terrain_container.N):
                movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
        valid = move_range_person.calc_move([], uncross, movmap, pos, mov, self.terrain_container.M,
                                              self.terrain_container.N)
        mov_range=[]
        att_range=set()
        diff_range=[]
        minr = 255
        maxr = -255
        for i in p.item:
            if self.can_equip(pid, i):
                if minr > i.itemtype.min_range:
                    minr = i.itemtype.min_range
                if maxr < i.itemtype.max_range:
                    maxr = i.itemtype.max_range
        for item in valid:
            mov_range.append(item)
        for i in range(self.terrain_container.M):
            for j in range(self.terrain_container.N):
                for item in mov_range:
                    d=calc_dist((i,j),item)
                    if d>=minr and d<=maxr:
                        att_range.add((i,j))
                        if not (i,j) in mov_range:
                            diff_range.append((i,j))
        return mov_range,att_range,diff_range

    def collective_range(self):
        range=set()
        for p in self.person_container.position:
            if self.person_container.controller[p]==1:
                range=range|self.move_and_attack_range(p)[1]
        return range

    def send_mapstate(self):
        valid={}                       #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        invalid={}                     #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        ally={}                        #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        enemy={}                       #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        if self.controller==0:
            for p in self.person_container.people:
                if self.person_container.controller[p.pid]==0:
                    if self.person_container.movable[p.pid]:
                        unstable=[]
                        uncross=[]
                        pos=self.person_container.position[p.pid]
                        mov=p.ability["MOV"]
                        for other in self.person_container.people:
                            if not (p==other):
                                if self.person_container.controller[other.pid]==0:
                                    unstable.append(self.person_container.position[other.pid])
                                elif self.person_container.controller[other.pid]==1:
                                    uncross.append(self.person_container.position[other.pid])
                                else:
                                    unstable.append(self.person_container.position[other.pid])
                        #movmap=numpy.zeros((self.terrain_container.M,self.terrain_container.N))
                        movmap={}
                        for i in range(self.terrain_container.M):
                            for j in range(self.terrain_container.N):
                                movmap[(i,j)]=self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                        dstlist=move_range_person.calc_move(unstable,uncross,movmap,pos,mov,self.terrain_container.M,self.terrain_container.N)
                        valid[p.pid]=dstlist
                    else:
                        invalid[p.pid]={self.person_container.position[p.pid]:(float(0),[self.person_container.position[p.pid]])}
                elif self.person_container.controller[p.pid]==1:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                uncross.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                unstable.append(self.person_container.position[other.pid])
                            else:
                                uncross.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    enemy[p.pid]=dstlist
                else:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                unstable.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                uncross.append(self.person_container.position[other.pid])
                            else:
                                unstable.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    ally[p.pid]=dstlist
            return valid, invalid, ally, enemy
        if self.controller==1:
            for p in self.person_container.people:
                if self.person_container.controller[p.pid]==1:
                    if self.person_container.movable[p.pid]:
                        unstable=[]
                        uncross=[]
                        pos=self.person_container.position[p.pid]
                        mov=p.ability["MOV"]
                        for other in self.person_container.people:
                            if not (p==other):
                                if self.person_container.controller[other.pid]==0:
                                    uncross.append(self.person_container.position[other.pid])
                                elif self.person_container.controller[other.pid]==1:
                                    unstable.append(self.person_container.position[other.pid])
                                else:
                                    uncross.append(self.person_container.position[other.pid])
                        #movmap=numpy.zeros((self.terrain_container.M,self.terrain_container.N))
                        movmap={}
                        for i in range(self.terrain_container.M):
                            for j in range(self.terrain_container.N):
                                movmap[(i,j)]=self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                        dstlist=move_range_person.calc_move(unstable,uncross,movmap,pos,mov,self.terrain_container.M,self.terrain_container.N)
                        valid[p.pid]=dstlist
                    else:
                        invalid[p.pid]={self.person_container.position[p.pid]:(float(0),[self.person_container.position[p.pid]])}
                elif self.person_container.controller[p.pid]==0:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                unstable.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                uncross.append(self.person_container.position[other.pid])
                            else:
                                unstable.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    enemy[p.pid]=dstlist
                else:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                unstable.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                uncross.append(self.person_container.position[other.pid])
                            else:
                                unstable.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    enemy[p.pid]=dstlist
            return valid, self.global_vars.AIcontroller.enemy_single_movement(valid,invalid,ally,enemy,self)
        if self.controller == 2:
            for p in self.person_container.people:
                if self.person_container.controller[p.pid] == 2:
                    if self.person_container.movable[p.pid]:
                        unstable = []
                        uncross = []
                        pos = self.person_container.position[p.pid]
                        mov = p.ability["MOV"]
                        for other in self.person_container.people:
                            if not (p == other):
                                if self.person_container.controller[other.pid] == 0:
                                    unstable.append(self.person_container.position[other.pid])
                                elif self.person_container.controller[other.pid] == 1:
                                    uncross.append(self.person_container.position[other.pid])
                                else:
                                    unstable.append(self.person_container.position[other.pid])
                        #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                        movmap={}
                        for i in range(self.terrain_container.M):
                            for j in range(self.terrain_container.N):
                                movmap[(i, j)] = self.terrain_container.map[i][j].decay[
                                    self.global_vars.data.cls_clsgroup[p.cls]]
                        dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                        valid[p.pid] = dstlist
                    else:
                        invalid[p.pid] = {
                            self.person_container.position[p.pid]: (float(0), [self.person_container.position[p.pid]])}
                elif self.person_container.controller[p.pid] == 1:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                uncross.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                unstable.append(self.person_container.position[other.pid])
                            else:
                                uncross.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    enemy[p.pid] = dstlist
                else:
                    unstable = []
                    uncross = []
                    pos = self.person_container.position[p.pid]
                    mov = p.ability["MOV"]
                    for other in self.person_container.people:
                        if not (p == other):
                            if self.person_container.controller[other.pid] == 0:
                                unstable.append(self.person_container.position[other.pid])
                            elif self.person_container.controller[other.pid] == 1:
                                uncross.append(self.person_container.position[other.pid])
                            else:
                                unstable.append(self.person_container.position[other.pid])
                    #movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    movmap={}
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[(i, j)] = self.terrain_container.map[i][j].decay[self.global_vars.data.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov,self.terrain_container.M,self.terrain_container.N)
                    ally[p.pid] = dstlist
            return valid, self.global_vars.AIcontroller.enemy_single_movement(valid,invalid,ally,enemy,self)

    def reset_state(self,cont):
        for p in self.person_container.people:
            if self.person_container.controller[p.pid]==cont:
                self.person_container.movable[p.pid]=True
        return

    def drive_map(self):
        while self.turn<=5:
            self.turn+=1
            print("TURN.%d"%(self.turn))
            print("Player Phase")
            while True:
                command=self.send_mapstate()
                print(command)
                command_type=command[0]      #type:str
                if command_type=="M":
                    person_to_move=command[1]  #type:person.Person
                    pos_to_move=command[2]
                    self.person_container.position[person_to_move.pid]=pos_to_move
                    self.person_container.movable[person_to_move.pid]=False


                elif command_type=="E":
                    if self.controller==0:
                        self.reset_state(0)
                        self.controller=1
                        print("Enemy Phase")
                    elif self.controller==1:
                        self.reset_state(1)
                        self.controller=0
                        break
                    else:
                        pass
                else:
                    pass

    def ai_turn(self, arena):
        valid, command = self.send_mapstate()
        for cmd in command:
            print(cmd)
        command_type = command[0]
        if command_type == "M":
            person_to_move = command[1]  # type:person.Person
            arena.set_mapstate(valid[person_to_move.pid], 'in_enemy_moverange')
            arena.move(command[1], command[3])

        elif command_type == "E":
            self.reset_state(1)
            self.controller = 0
            print('player phase')
            arena.next_round()

    def take_turn(self, arena):
        if self.controller is not 0:
            self.ai_turn2(arena)
        else:
            arena.player_turn()

    def ai_turn2(self, arena):
        valid, command = self.send_mapstate()
        command_type = command[0]
        print(command)
        if command_type == "M":
            person_to_move = command[1].pid  # type:person.Person
            arena.focus(person_to_move)
            arena.move(pid=person_to_move, dst=command[3], vld=valid)
        elif command_type == "E":
            self.reset_state(self.controller)
            self.controller += 1
            if self.controller == 3:
                print('player phase')
                arena.next_round()
            else:
                count, armylist = self.count_army_population()
                if count[2] == 0:
                    self.send_mapstate()
                    print('player phase')
                    arena.next_round()
                else:
                    print('ally phase')
                    arena.ai_phase()

        elif command_type == "A":
            person_to_move = command[1].pid
            arena.focus(person_to_move)
            battlelist = [command[1], command[4], command[5], self, command[3][-1]]
            arena.attacking(pid=person_to_move, dst=command[3], vld=valid, battlelist=battlelist)

    def attackable(self, weapon):
        return weapon in self.global_vars.data.attackable_weapon_types

    def can_support(self,pid,pos):
        sup_obj={}   #type:Dict[str,Tuple[int,int]]
        p=self.global_vars.personBank[pid]
        for obj in p.suprank:
            if obj in self.person_container.position:
                if self.person_container.controller[obj]==0:
                    if calc_dist(pos,self.person_container.position[obj])<2:
                        if (p.supdata[obj][0]>=50)and(p.suprank[obj]<1):
                            sup_obj[obj]=self.person_container.position[obj]
                        if (p.supdata[obj][0]>=100)and(p.suprank[obj]<2):
                            sup_obj[obj] = self.person_container.position[obj]
                        if (p.supdata[obj][0]>=200)and(p.suprank[obj]<3):
                            sup_obj[obj]=self.person_container.position[obj]
        return sup_obj

    def build_support(self, pid1, pid2):
        p=self.global_vars.personBank[pid1]
        obj=self.global_vars.personBank[pid2]
        if (p.supdata[pid2][0] >= 50) and (p.suprank[pid2] < 1):
            p.suprank[pid2]=1
            obj.suprank[pid1]=1
            if pid1 in self.global_vars.data.support_text_map:
                if pid2 in self.global_vars.data.support_text_map[pid1]:
                    return self.global_vars.data.support_text_map[pid1][pid2]["C"]
            if pid2 in self.global_vars.data.support_text_map:
                if pid1 in self.global_vars.data.support_text_map[pid2]:
                    return self.global_vars.data.support_text_map[pid2][pid1]["C"]
            return []
        if (p.supdata[pid2][0] >= 100) and (p.suprank[pid2] < 2):
            p.suprank[pid2]=2
            obj.suprank[pid1]=2
            if pid1 in self.global_vars.data.support_text_map:
                if pid2 in self.global_vars.data.support_text_map[pid1]:
                    return self.global_vars.data.support_text_map[pid1][pid2]["B"]
            if pid2 in self.global_vars.data.support_text_map:
                if pid1 in self.global_vars.data.support_text_map[pid2]:
                    return self.global_vars.data.support_text_map[pid2][pid1]["B"]
            return []
        if (p.supdata[pid2][0] >= 200) and (p.suprank[pid2] < 3):
            p.suprank[pid2]=3
            obj.suprank[pid1]=3
            if pid1 in self.global_vars.data.support_text_map:
                if pid2 in self.global_vars.data.support_text_map[pid1]:
                    return self.global_vars.data.support_text_map[pid1][pid2]["A"]
            if pid2 in self.global_vars.data.support_text_map:
                if pid1 in self.global_vars.data.support_text_map[pid2]:
                    return self.global_vars.data.support_text_map[pid2][pid1]["A"]
            return []
        return []

    def defeated_character(self,pid):
        self.person_container.position.pop(pid)
        self.person_container.movable.pop(pid)
        c=self.person_container.controller.pop(pid)
        self.person_container.army.pop(pid)
        self.person_container.AItype.pop(pid)
        if (c==0):
            if pid in self.global_vars.player_character_status:
                if self.global_vars.player_character_status[pid]==1:
                    self.global_vars.player_character_status[pid]=2

        for p in self.person_container.people:
            if p.pid == pid:
                self.person_container.people.remove(p)
                return

    def exchange_item(self,p1,p2,i1,i2):
        if (p1==p2)and(i1==i2):
            return
        person1=self.global_vars.personBank[p1]
        person2=self.global_vars.personBank[p2]
        if i1<len(person1.item):
            item1=person1.item[i1]
        else:
            item1=None
        if i2<len(person2.item):
            item2=person2.item[i2]
        else:
            item2=None
        if item1==None:
            if item2==None:
                return
            if (person2.get_equip()==item2):
                person2.dequip(item2)
            person2.item.remove(item2)
            person1.item.append(item2)
            return
        if item2==None:
            if (person1.get_equip()==item1):
                person1.dequip(item1)
            person1.item.remove(item1)
            person2.item.append(item1)
            return
        if (person1.get_equip()==item1):
            person1.dequip(item1)
        if (person2.get_equip()==item2):
            person2.dequip(item2)
        person1.item.remove(item1)
        person2.item.remove(item2)
        person1.item.insert(i1,item2)
        person2.item.insert(i2,item1)
        return

    def can_rescue(self,pid,pos):
        cry_obj={}   #type:Dict[str,Tuple[int,int]]
        p=self.global_vars.personBank[pid]
        for obj in self.person_container.position:
            if (self.person_container.controller[obj]==0) or (self.person_container.controller[obj]==2):
                if calc_dist(pos,self.person_container.position[obj])==1:
                    if self.global_vars.personBank[obj].ability["BLD"]<=p.ability["CRY"]:
                        cry_obj[obj]=self.person_container.position[obj]
        return cry_obj

    def can_use(self, pid, item):
        if item.itemtype.use_effect=="UNAVAILABLE":
            return False
        if item.itemtype.use_effect.split(" ")[0]=="HEAL":
            if self.global_vars.personBank[pid].ability["HP"]>=self.global_vars.personBank[pid].ability["MHP"]:
                return False
        if "PROMOTE" in item.itemtype.use_effect.split(" "):
            if len(self.global_vars.personBank[pid].can_promote(self.global_vars))==0:
                return False
        if len(item.itemtype.character_only)>0:
            if not pid in item.itemtype.character_only:
                return False
        return True

    def can_equip(self, pid, item):
        if not item.itemtype.weapontype in ["Sword","Bow","Axe","Lance","Light","Dark","Wind","Fire","Thunder"]:
            return False
        if item.itemtype.rank>self.global_vars.personBank[pid].weapon_rank[item.itemtype.weapontype]:
            return False
        if len(item.itemtype.character_only)>0:
            if not pid in item.itemtype.character_only:
                return False
        return True

    def can_banish(self, pid, item):
        if item.itemtype.cannot_banish==1:
            return False
        return True

    def find_attackable(self,pid,pos):
        person=self.global_vars.personBank[pid]
        minr=255
        maxr=-255
        enemy_list=[]
        for i in person.item:
            if self.can_equip(pid,i):
                if minr>i.itemtype.min_range:
                    minr=i.itemtype.min_range
                if maxr<i.itemtype.max_range:
                    maxr=i.itemtype.max_range
        for p in self.person_container.position:
            if p==pid:
                continue
            if (self.person_container.controller[p]%2==self.person_container.controller[pid]%2):
                continue
            d=calc_dist(self.person_container.position[p],pos)
            if (d>=minr)and(d<=maxr):
                enemy_list.append(p)
        return enemy_list

    def get_attack_range(self,pid,valid):
        available_blocks=set()
        differential_blocks=set()
        person = self.global_vars.personBank[pid]
        minr = 255
        maxr = -255
        unstablevalid=self.unstable_valid_grid(pid)
        for i in person.item:
            if self.can_equip(pid,i):
                if minr>i.itemtype.min_range:
                    minr=i.itemtype.min_range
                if maxr<i.itemtype.max_range:
                    maxr=i.itemtype.max_range
        for i in range(self.terrain_container.M):
            for j in range(self.terrain_container.N):
                for ppos in valid[pid]:
                    d=calc_dist((i,j),ppos)
                    if (d>=minr)and(d<=maxr):
                        available_blocks.add((i,j))
                        if not (i,j) in valid[pid]:
                            if not (i,j) in unstablevalid:
                                differential_blocks.add((i,j))
        return available_blocks,differential_blocks,unstablevalid

    def get_attack_target(self,pid,valid):
        targets={}
        for ppos in valid[pid]:
            enemies=self.find_attackable(pid,ppos)
            for enemy in enemies:
                if enemy in targets:
                    targets[enemy].append(ppos)
                else:
                    targets[enemy]=[ppos]
        return targets

    def available_wand(self,pid):
        wands=[]
        p=self.global_vars.personBank[pid]
        if "Silence" in p.status:
            return wands
        for i in p.item:
            if i.itemtype.weapontype=="Wand":
                if i.itemtype.rank<=p.weapon_rank["Wand"]:
                    wands.append(i)
        return wands

    def send_to_transporter(self,_item):
        self.global_vars.transporter[_item.itemtype.weapontype].append(_item)
        return

    def find_nearest_empty_block(self,pos,as_blank=[],as_occupied=[]):
        _map = []
        for i in range(self.terrain_container.M):
            _row = []
            for j in range(self.terrain_container.N):
                _row.append(0)
            _map.append(_row)
            del (_row)
        for p in self.person_container.position:
            _map[self.person_container.position[p][0]][self.person_container.position[p][1]]=1
        for _pos in as_blank:
            _map[_pos[0]][_pos[1]]=0
        for _pos in as_occupied:
            _map[_pos[0]][_pos[1]]=1
        dmax=-1
        retmap={}
        for i in range(self.terrain_container.M):
            for j in range(self.terrain_container.N):
                if (_map[i][j]==0):
                    d=calc_dist((i,j),pos)
                    if d in retmap:
                        retmap[d].append((i,j))
                    else:
                        if (d>dmax):
                            dmax=d
                        retmap[d]=[(i,j)]
        if dmax==-1:
            return (-1,-1)
        for i in range(0,dmax):
            if i in retmap:
                candidates=retmap[i]
                return candidates[0]

    def get_grid_event(self,pos,p):
        if self.terrain_container.map[pos[0]][pos[1]].typename=="Village":
            event=None
            if not("%d,%d"%pos in self.eventlist["Villages"]):
                return ("V",None)
            candidates=self.eventlist["Villages"]["%d,%d"%pos]
            for candidate in candidates:
                ch=candidate["Character"]
                cd=candidate["Condition"]
                if not(ch==p):
                    if not(ch==None):
                        continue
                if check_condition(cd,self) == True:
                    event=candidate
                    break
            return ("V",event)
        elif self.terrain_container.map[pos[0]][pos[1]].typename=="Treasury":
            event=None
            if not("%d,%d"%pos in self.eventlist["Treasures"]):
                return ("T",None,None)
            event=self.eventlist["Treasures"]["%d,%d"%pos]
            person=self.global_vars.personBank[p]
            if person.cls=="Rogue":
                return ("T",event,None)
            if self.global_vars.clsBank[person.cls].cls_group=="Cracksman":
                for _i in person.item:
                    if _i.itemtype.name=="Lockpick":
                        return ("T",event,_i)
            for _i in person.item:
                if _i.itemtype.name=="Chestkey":
                    return ("T",event,_i)
        return ("N",None)

    def have_exchange_object(self,pid,pos):
        exchange_objects=[]
        for p in self.person_container.position:
            if self.person_container.controller[p]==self.person_container.controller[pid]:
                if calc_dist(self.person_container.position[p],pos)==1:
                    if not p==pid:
                        exchange_objects.append(p)
        return exchange_objects

    def have_items(self,pid):
        person=self.global_vars.personBank[pid]
        if len(person.item)<1:
            return False
        return True

    def get_seize_event(self,pid,pos):
        if not ("%d,%d" % pos in self.eventlist["Seize"]):
            return None
        event = None
        candidates = self.eventlist["Seize"]["%d,%d" % pos]
        for candidate in candidates:
            ch = candidate["Character"]
            cd = candidate["Condition"]
            if not (ch == pid):
                if not (ch == None):
                    continue
            if check_condition(cd, self) == True:
                event = candidate
                break
        return event

    def map_reconstruct(self,rec):
        x=rec["Anchor_X"]
        y=rec["Anchor_Y"]
        m=rec["M"]
        n=rec["N"]
        map_new=rec["Map"]
        for i in range(m):
            for j in range(n):
                self.terrain_container.map[i+x][j+y]\
                    =self.global_vars.terrainBank[map_new[i][j]]
        return

    def can_steal(self,pid,pos):
        person=self.global_vars.personBank[pid]
        if not (self.global_vars.clsBank[person.cls].cls_group=="Cracksman"):
            return {}
        obj={}
        for p in self.person_container.position:
            if self.person_container.controller[p]%2==self.person_container.controller[pid]%2:
                continue
            if person.ability["SPD"]<=self.global_vars.personBank[p].ability["SPD"]:
                continue
            if not calc_dist(pos,self.person_container.position[p])==1:
                continue
            ilist=[]
            for _i in self.global_vars.personBank[p].item:
                if not _i==self.global_vars.personBank[p].get_equip():
                    if _i.itemtype.weight<=person.ability["CRY"]:
                        ilist.append(_i)
            obj[p]=ilist
            del(ilist)
        return obj

    def unlock_door(self,pos,p):
        doors={}
        x=pos[0]
        y=pos[1]
        item=None
        has_key=0
        person=self.global_vars.personBank[p]
        if person.cls=="Rogue":
            has_key=1
        elif self.global_vars.clsBank[person.cls].cls_group=="Cracksman":
            for _i in person.item:
                if _i.itemtype.name=="Lockpick":
                    item=_i
                    has_key=1
            if has_key==0:
                for _i in person.item:
                    if _i.itemtype.name=="Doorkey":
                        item=_i
                        has_key=1
        else:
            for _i in person.item:
                if _i.itemtype.name=="Doorkey":
                    item=_i
                    has_key=1
        if has_key==0:
            return (doors,None)
        if x-1>=0:
            if self.terrain_container.map[x-1][y].typename=="Door":
                if ("%d,%d"%(x-1,y) in self.eventlist["Doors"]):
                    for event in self.eventlist["Doors"]["%d,%d"%(x-1,y)]:
                        if check_condition(event["Condition"],self):
                            doors[(x-1,y)]=event
                            break
        if x+1<self.terrain_container.M:
            if self.terrain_container.map[x+1][y].typename=="Door":
                if ("%d,%d"%(x+1,y) in self.eventlist["Doors"]):
                    for event in self.eventlist["Doors"]["%d,%d"%(x+1,y)]:
                        if check_condition(event["Condition"],self):
                            doors[(x+1,y)]=event
                            break
        if y-1>=0:
            if self.terrain_container.map[x][y-1].typename=="Door":
                if ("%d,%d"%(x,y-1) in self.eventlist["Doors"]):
                    for event in self.eventlist["Doors"]["%d,%d"%(x,y-1)]:
                        if check_condition(event["Condition"],self):
                            doors[(x,y-1)]=event
                            break
        if y+1<self.terrain_container.N:
            if self.terrain_container.map[x][y+1].typename=="Door":
                if ("%d,%d"%(x,y+1) in self.eventlist["Doors"]):
                    for event in self.eventlist["Doors"]["%d,%d"%(x,y+1)]:
                        if check_condition(event["Condition"],self):
                            doors[(x,y+1)]=event
                            break
        return (doors,item)

    def find_talk_obj(self,pid,pos):
        objs={}
        for obj in self.person_container.position:
            if not calc_dist(pos,self.person_container.position[obj])==1:
                continue
            if "Silence" in self.global_vars.personBank[obj].status:
                continue
            for event in self.eventlist["Dialogs"]:
                ch_satisfied=0
                for chtp in event["Character"]:
                    if str(pid)==chtp[0] and str(obj)==chtp[1]:
                        ch_satisfied=1
                        break
                if ch_satisfied==0:
                    continue
                if not check_condition(event["Condition"],self):
                    continue
                if not obj in objs:
                    objs[obj]=event
        return objs

    def refresh_person(self,pid):
        #print(pid)
        pos=self.person_container.position[pid]
        person=self.global_vars.personBank[pid]
        #print(person.status)
        hp_recov=0
        sta_clear=[]
        log=[]
        if self.terrain_container.map[pos[0]][pos[1]].typename=="Fort":
            hp_recov=5
            if "Sleep" in person.status:
                person.status.pop("Sleep")
                sta_clear.append("Sleep")
            if "Berserk" in person.status:
                person.status.pop("Berserk")
                sta_clear.append("Berserk")
            if "Stone" in person.status:
                person.status.pop("Stone")
                sta_clear.append("Stone")
            if "Poison" in person.status:
                person.status.pop("Poison")
                sta_clear.append("Poison")
            if "Silence" in person.status:
                person.status.pop("Silence")
                sta_clear.append("Silence")
        elif self.terrain_container.map[pos[0]][pos[1]].typename=="Gate":
            hp_recov=10
            if "Sleep" in person.status:
                person.status.pop("Sleep")
                sta_clear.append("Sleep")
            if "Berserk" in person.status:
                person.status.pop("Berserk")
                sta_clear.append("Berserk")
            if "Stone" in person.status:
                person.status.pop("Stone")
                sta_clear.append("Stone")
            if "Poison" in person.status:
                person.status.pop("Poison")
                sta_clear.append("Poison")
            if "Silence" in person.status:
                person.status.pop("Silence")
                sta_clear.append("Silence")
        elif self.terrain_container.map[pos[0]][pos[1]].typename=="Throne":
            hp_recov=10
            if "Sleep" in person.status:
                person.status.pop("Sleep")
                sta_clear.append("Sleep")
            if "Berserk" in person.status:
                person.status.pop("Berserk")
                sta_clear.append("Berserk")
            if "Stone" in person.status:
                person.status.pop("Stone")
                sta_clear.append("Stone")
            if "Poison" in person.status:
                person.status.pop("Poison")
                sta_clear.append("Poison")
            if "Silence" in person.status:
                person.status.pop("Silence")
                sta_clear.append("Silence")
        #if "Recover" in person.skills
        if hp_recov>person.ability["MHP"]-person.ability["HP"]:
            hp_recov=person.ability["MHP"]-person.ability["HP"]
        if hp_recov>0:
            person.ability["HP"]+=hp_recov
            log.append(('Heal',hp_recov))
        if "Poison" in person.status:
            hp_poi=int(person.ability["MHP"]/8)
            if hp_poi>=person.ability["HP"]:
                hp_poi=person.ability["HP"]-1
            if hp_poi>=1:
                person.ability["HP"]-=hp_poi
                log.append(('Poison',hp_poi))
        for sta in list(person.status.keys()).copy():
            person.status[sta]-=1
            if sta=="Barrier":
                person.ability["RES"]-=1
            if person.status[sta]<1:
                person.status.pop(sta)
                sta_clear.append(sta)
        for sta in sta_clear:
            log.append(('Relief',sta))
        self.person_container.movable[pid]=True
        for obj in person.supdata:
            if obj in self.person_container.position:
                if self.person_container.controller[obj]==self.person_container.controller[pid]:
                    if calc_dist(self.person_container.position[obj],pos)<2:
                        if person.suprank[obj]==3:
                            continue
                        if (person.suprank[obj]==2)and(person.supdata[obj][0]<200):
                            person.supdata[obj][0]+=person.supdata[obj][1]
                            continue
                        if (person.suprank[obj]==1)and(person.supdata[obj][0]<100):
                            person.supdata[obj][0]+=person.supdata[obj][1]
                            continue
                        if (person.suprank[obj]==0)and(person.supdata[obj][0]<50):
                            person.supdata[obj][0]+=person.supdata[obj][1]
                            continue
        if 'Sleep' in person.status:
            self.person_container.movable[pid]=False
        #print(log)
        return log

    def reinforce_person(self,pid,controller,pos,army,pri,strategy):
        #print("REINFORCEMENT No.%s"%(pid))
        person=self.global_vars.personBank[pid]
        self.person_container.people.append(person)
        pos_real=self.find_nearest_empty_block(pos)
        self.person_container.controller[pid]=controller
        self.person_container.position[pid]=pos_real
        self.person_container.movable[pid]=True
        self.person_container.army[pid]=army
        self.person_container.AItype[pid]=(pri,self.global_vars.data.ai_configs[strategy])
        return

    def count_army_population(self):
        count=[0,0,0,0]
        armylist=[{},{},{},{}]
        for pid in self.person_container.controller:
            c=self.person_container.controller[pid]
            count[c]+=1
            if not self.person_container.army[pid] in armylist[c]:
                armylist[c][self.person_container.army[pid]]=1
            else:
                armylist[c][self.person_container.army[pid]]+=1
        return (count,armylist)

    def get_thumbnail(self):
        m=self.terrain_container.M
        n=self.terrain_container.N
        minimap={}
        for i in range(m):
            for j in range(n):
                minimap[(m,n)]=-1
        for p in self.person_container.position:
            pos=self.person_container.position[p]
            minimap[pos]=self.person_container.controller[p]
        return minimap

    def map_save(self):
        return self.global_vars.map_save("game_0.sav",0)

    def map_load(self):
        return self.global_vars.map_load("map_save.sav")








