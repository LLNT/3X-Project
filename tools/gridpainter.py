import numpy
import cv2
c=(255,0,0)
m=100
n=100
m1=(m-1)/2
n1=(n-1)/2
if m%2==0:
    m2=m1+1
else:
    m2=m1
if n%2==0:
    n2=n1+1
else:
    n2=n1
grid=numpy.zeros((m,n,3),dtype="uint8")
for i in range(m):
    for j in range(n):
        if min(abs(i-m1),abs(i-m2))+min(abs(j-n1),abs(j-n2))<min(m1,m2):
            #print(i,j)
            grid[i,j]=c
#print(grid)
cv2.imwrite("grid_0.jpg",grid)
