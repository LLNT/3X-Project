import numpy as np
import cv2
m=18
n=15
c=(134,132,133)
mat=np.zeros((80*m,80*n,3),dtype="uint8")
for i in range(m):
    for j in range(n):
        cv2.rectangle(mat,(80*i,80*j),(80,80),c)
cv2.imwrite("blocks.jpg",mat)
