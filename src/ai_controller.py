from typing import List,Tuple
import random
import map_controller
class AI_Controller:
    def __init__(self):
        pass
    def enemy_single_movement(self,valid,invalid,ally,enemy,mapcontroller):
        valid=valid   #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        invalid=invalid #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        ally=ally    #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        enemy=enemy   #type:Dict[str,Dict[Tuple[int,int],Tuple[float,List[Tuple[int,int]]]]]
        mapcontroller=mapcontroller #type:map_controller.Main
        if len(valid)==0:
            return ["E",]
        person_to_move=random.choice(list(valid.keys()))
        dst_to_move_list=valid[person_to_move]
        dst_to_move=random.choice(list(dst_to_move_list.keys()))
        track_to_move=dst_to_move_list[dst_to_move][1]
        return ["M",mapcontroller.global_vars.personBank[person_to_move],dst_to_move,track_to_move]
