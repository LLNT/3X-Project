from typing import List,Tuple
import person
import random
class AI_Controller:
    def __init__(self):
        pass
    def enemy_single_movement(self,strategy_tuple):
        valid=strategy_tuple[0]   #type:List[Tuple[person.Person,List[Tuple[int,int]]]]
        invalid=strategy_tuple[1] #type:List[Tuple[person.Person,List[Tuple[int,int]]]]
        ally=strategy_tuple[2]    #type:List[Tuple[person.Person,List[Tuple[int,int]]]]
        enemy=strategy_tuple[3]   #type:List[Tuple[person.Person,List[Tuple[int,int]]]]
        if len(valid)==0:
            return ["E",]
        tomove=random.choice(valid)
        person_to_move=tomove[0]
        dst_to_move_list=tomove[1]
        dst_to_move=random.choice(list(dst_to_move_list.keys()))
        return ["M",person_to_move,dst_to_move]
