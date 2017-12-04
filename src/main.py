import numpy
import random

mov_map=numpy.zeros((15,15))
for i in range(15):
    for j in range(15):
        mov_map[i,j]=random.randint(1,5)
print(mov_map)
pos=(6,6)
mov=10
wait={}
dst={}
wait[pos]=10
while len(wait)>0:
    (tpos,r)=max(wait.items(),key=lambda x:x[1])
    dst[tpos]=r
    wait.pop(tpos)
    if tpos[0]>0:
        npos=(tpos[0]-1,tpos[1])
        if not (npos in dst):
            tr=r-mov_map[npos]
            if (tr>=0):
                if npos in wait:
                    r0=wait[npos]
                    if tr>r0:
                        wait[npos]=tr
                else:
                    wait[npos]=tr
    if tpos[0]<14:
        npos=(tpos[0]+1,tpos[1])
        if not (npos in dst):
            tr=r-mov_map[npos]
            if tr>=0:
                if npos in wait:
                    r0=wait[npos]
                    if tr>r0:
                        wait[npos]=tr
                else:
                    wait[npos]=tr
    if tpos[1]>0:
        npos=(tpos[0],tpos[1]-1)
        if not (npos in dst):
            tr=r-mov_map[npos]
            if tr>=0:
                if npos in wait:
                    r0=wait[npos]
                    if tr>r0:
                        wait[npos]=tr
                else:
                    wait[npos]=tr
    if tpos[1]<14:
        npos=(tpos[0],tpos[1]+1)
        if not (npos in dst):
            tr=r-mov_map[npos]
            if tr>=0:
                if npos in wait:
                    r0=wait[npos]
                    if tr>r0:
                        wait[npos]=tr
                else:
                    wait[npos]=tr
    print(tpos,r)
print(dst)
print("")
print("")
for i in range(15):
    row=""
    for j in range(15):
        row+=str(int(mov_map[i,j]))
        if (i,j)==pos:
            row+="$ "
        elif (i,j) in dst:
            #row+=str(int(dst[(i,j)]))
            row+="x "
        else:
            row+="  "
    print(row)
