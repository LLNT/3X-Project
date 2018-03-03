import json
mapname="map_1"
lines=open("%s.csv"%(mapname),"r").readlines()
n=len(lines)
m=len(lines[0].split(","))
mat=[]
d={}
for i in range(m):
    vec=[]
    for j in range(n):
        vec.append("")
    mat.append(vec)
    del(vec)
for i in range(n):
    line=lines[i].split(",")
    for j in range(m):
        block=line[j]
        block=block.replace("\n","")
        mat[j][n-i-1]=block
d["Name"]=mapname
d["M"]=m
d["N"]=n
d["Map"]=mat
f=open("%s.json"%(mapname),"w")
json.dump(d,f)
f.close()
