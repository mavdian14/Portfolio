import bisect

N = int(input())
s = []
x = []
length = 0
for i in range(0, N):
   tmp = input().strip().split(' ')
   a, b = [xx for xx in tmp]
   b = int(b) 
   if(a=="a"):
    bisect.insort(x, b)
    length += 1
   else:
    index = bisect.bisect_left(x, b)
    if index != length and x[index] == b:
        del x[index]
        length -=1
    else:
        print ("Wrong!")
        continue

   if(length<=0):
    print ("Wrong!")
    continue 
    
   nforme, nfm = divmod(length,2)
   nforme -= 1
   if(nfm>0):
    nforme += 1
    print(x[nforme])
   else:
    nfm = nforme + 1
    median = x[nforme] + x[nfm]
    median /= 2
    if(round(median)==median):
        median = round(median);
    print(median) 
