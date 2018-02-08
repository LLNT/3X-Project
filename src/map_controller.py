from typing import List,Dict,Tuple
import terrain_container
import person_container
import move_range_person
import global_vars
import person
import numpy
from utility import *

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
    def __init__(self,terrain_map,person_container,glb):
        self.terrain_container=terrain_map
        self.person_container=person_container
        self.turn=0
        self.controller=0
        self.global_vars=glb
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
                        movmap=numpy.zeros((self.terrain_container.M,self.terrain_container.N))
                        for i in range(self.terrain_container.M):
                            for j in range(self.terrain_container.N):
                                movmap[i,j]=self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                        dstlist=move_range_person.calc_move(unstable,uncross,movmap,pos,mov)
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
                    movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov)
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
                    movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov)
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
                        movmap=numpy.zeros((self.terrain_container.M,self.terrain_container.N))
                        for i in range(self.terrain_container.M):
                            for j in range(self.terrain_container.N):
                                movmap[i,j]=self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                        dstlist=move_range_person.calc_move(unstable,uncross,movmap,pos,mov)
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
                    movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov)
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
                    movmap = numpy.zeros((self.terrain_container.M, self.terrain_container.N))
                    for i in range(self.terrain_container.M):
                        for j in range(self.terrain_container.N):
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.global_vars.cls_clsgroup[p.cls]]
                    dstlist = move_range_person.calc_move(unstable, uncross, movmap, pos, mov)
                    enemy[p.pid]=dstlist
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
        print(command)
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

    def player_turn(self, arena):

        arena.is_event_handler = True

    def take_turn(self, arena):
        if self.controller == 0:
            self.player_turn(arena)
        else:
            self.ai_turn2(arena)

    def ai_turn2(self, arena):
        valid, command = self.send_mapstate()
        command_type = command[0]
        print(command)
        if command_type == "M":
            person_to_move = command[1].pid  # type:person.Person
            arena.enemy_move(person_to_move, command[3], valid[person_to_move])

        elif command_type == "E":
            self.reset_state(1)
            self.controller = 0
            print('player phase')
            arena.next_round()

        elif command_type == "A":
            person_to_move = command[1].pid
            arena.enemy_move(person_to_move, command[3], valid[person_to_move])

    def attackable(self, weapon):
        return weapon in self.global_vars.attackable_weapon_types

    def can_support(self,pid,pos):
        sup_obj={}   #type:Dict[str,Tuple[int,int]]
        p=self.global_vars.personBank[pid]
        for obj in p.suprank:
            if obj in self.person_container.position:
                if self.person_container.controller[obj]==0:
                    if calc_dist(pos,self.person_container.position[obj])<2:
                        if (p.supdata[obj][0]>50)and(p.suprank[obj]<1):
                            sup_obj[obj]=self.person_container.position[obj]
                        if (p.supdata[obj][0]>100)and(p.suprank[obj]<2):
                            sup_obj[obj] = self.person_container.position[obj]
                        if (p.supdata[obj][0]>200)and(p.suprank[obj]<3):
                            sup_obj[obj]=self.person_container.position[obj]
        return sup_obj

    def build_support(self, pid1, pid2):
        p=self.global_vars.personBank[pid1]
        obj=self.global_vars.personBank[pid2]
        if (p.supdata[pid2][0] > 50) and (p.suprank[pid2] < 1):
            p.suprank[pid2]=1
            obj.suprank[pid1]=1
            return
        if (p.supdata[pid2][0] > 100) and (p.suprank[pid2] < 2):
            p.suprank[pid2]=2
            obj.suprank[pid1]=2
            return
        if (p.supdata[pid2][0] > 200) and (p.suprank[pid2] < 3):
            p.suprank[pid2]=3
            obj.suprank[pid1]=3
            return
        return

    def defeated_character(self,pid):
        self.person_container.position.pop(pid)
        self.person_container.movable.pop(pid)
        c=self.person_container.controller.pop(pid)
        if (c==0):
            if self.global_vars.player_character_status[pid]==1:
                self.global_vars.player_character_status[pid]=2

        for p in self.person_container.people:
            if p.pid == pid:
                self.person_container.people.remove(p)
                return