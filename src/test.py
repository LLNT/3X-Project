import move_range_person as mrp
import numpy
from global_vars import Main as Global
from data_loader import Main as Data
from terrain_container import Main as Terrain_Container
from person_container import Main as Person_Container
import map_controller
import battle
if __name__ == '__main__':
    mov_map = numpy.random.randint(1,5,(15, 15))
    pos = (2, 3)
    mov = 10
    unstable=set([(1,2),(5,6)])
    uncross=set([(4,5),(2,2)])
    print(mrp.calc_move(unstable,uncross,mov_map,pos,mov))
    data=Data()
    global_vars=Global(data)
    global_vars.saved_data_preload()
    print("AAAAAAAAAAAAAAAAAAAA")
    print(global_vars.terrainBank["Forest"].enhance)
    print(global_vars.clsBank["Lord"].weapon_rank)
    print(global_vars.personBank["1"].ability)
    terrain_container_test=Terrain_Container(data.terrain_map,global_vars.terrainBank)
    person_container_test=Person_Container(data.map_armylist,global_vars.personBank)
    map1=map_controller.Main(terrain_container_test,person_container_test,global_vars)
    print(global_vars.itemtypeBank["Iron Lance"].ability_bonus)
    print(global_vars.itemBank[1].itemtype.weapontype)
    print(global_vars.personBank["1"].item[1].itemtype.name)
    print(global_vars.personBank["1"].weapon_rank)
    print(battle.Battle(global_vars.personBank["1"],global_vars.personBank["2"],
                        global_vars.personBank["1"].item[0],global_vars.personBank["2"].item[0],
                        map1,(0,3)).battle())
    print(global_vars.personBank["1"].suprank)
    print(battle.Battle(global_vars.personBank["1"], global_vars.personBank["4"],
                        global_vars.personBank["1"].item[0], global_vars.personBank["4"].item[0],
                        map1, (0, 1)).battle())
    #map1.drive_map()