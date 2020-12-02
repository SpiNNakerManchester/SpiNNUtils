import random
import time
from spinn_utilities.unigue_list import UnigueList
from spinn_utilities.set_list import SetList
from spinn_utilities.ordered_set import OrderedSet

#data = [random.randint(1, 10000) for i in range(100000)]
data = range(100000)
start = time.time()
ul = UnigueList()
for foo in data:
    ul.append(foo)
print(len(ul))
print (time.time()-start)
start = time.time()
os = OrderedSet()
for foo in data:
    os.add(foo)
print(len(os))
print (time.time()-start)
start = time.time()
sl = SetList()
for foo in data:
    sl.add(foo)
print(len(sl))
print (time.time()-start)
