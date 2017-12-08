from typing import List,Dict
class Test:
    def __init__(self):
        self.val=0
    def __init__(self,x):
        self.val=x #type:int
    def get_val(self):
        return self.val

l=[] #type:List[Test]
d={} #type:Dict[int,Test]
for i in range(5):
    d[int(i)]=Test(i)
for i in range(5):
    l.append(d[int(i)])
for item in l:
    print(item.get_val())
    print(d[int(i)].get_val())
