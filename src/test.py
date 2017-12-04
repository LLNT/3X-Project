import move_range_person as mrp
import numpy
mov_map = numpy.random.randint(1,5,(15, 15))
pos = (2, 3)
mov = 10
unstable=set([(1,2),(5,6)])
uncross=set([(4,5),(2,2)])
print(mrp.calc_move(unstable,uncross,mov_map,pos,mov))
