from typing import List
import terrain_container
import person_container
import move_range_person
import data_loader
import numpy
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
        self.data=None                  #type:data_loader.Main
        self.turn=0
        self.controller=0
    def __init__(self,terrain_map,person_container,data):
        self.terrain_container=terrain_map
        self.person_container=person_container
        self.turn=0
        self.controller=0
        self.data=data
    def send_mapstate(self):
        valid=[]
        invalid=[]
        ally=[]
        enemy=[]
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
                                movmap[i,j]=self.terrain_container.map[i][j].decay[self.data.cls_clsgroup[p.cls]]
                        dstlist=list(move_range_person.calc_move(unstable,uncross,movmap,pos,mov))
                        valid.append((p,dstlist))
                    else:
                        invalid.append((p,[]))
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
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.data.cls_clsgroup[p.cls]]
                    dstlist = list(move_range_person.calc_move(unstable, uncross, movmap, pos, mov))
                    enemy.append((p,dstlist))
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
                            movmap[i, j] = self.terrain_container.map[i][j].decay[self.data.cls_clsgroup[p.cls]]
                    dstlist = list(move_range_person.calc_move(unstable, uncross, movmap, pos, mov))
                    ally.append((p,dstlist))
        execute(valid,invalid,ally,enemy)

