# Enter your code here. Read input from STDIN. Print output to STDOUT
from heapq import heappush, heappop

#initialize the variables
heap = []
lookup = set()

for i in range(int(input())):
    t = list(map(int, input().split()))
    
    if t[0] == 1:
        #heap command to add an element to a heap 
        heappush(heap, t[1])
        #.add() is used for sets to add an element to a set
        lookup.add(t[1])
    
    elif t[0] == 2:
        #.discard() removes element from a set
        lookup.discard(t[1])
    
    else:
        #will delete min elements until its also in the lookup set. In a heap, the minimum is always at the root of the heap i.e. heap[0]
        while heap[0] not in lookup:
            heappop(heap)
        
        print(heap[0])
    
    
