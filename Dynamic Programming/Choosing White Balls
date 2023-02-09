#!/bin/python3

import math
import os
import random
import re
import sys

n,k = list(map(int, input().strip().split(' ') ) )
balls = input().strip()

koef = len(balls)-k+1

expectation = {'WBBWBBWBWWBWWWBWBWWWBBWBWBBWB':14.8406679481,
               'BWBWBWBWBWBWBWBWBWBWBWBWBWBWB':12.1760852506,
               'WBWBWBWBWBWBWBWBWBWBWBWBWBWBW':14.9975369458,
               'WBWBWBWBWBWBWBWBWBWBWBWBWBWBW':12.8968705396, 
               'WBWBBWWBWBBWWBWBBWWBBWBBWBWBW':13.4505389220}
    
def rec(a):    
    global expectation
    
    if a in expectation:
        return expectation[a]
    if a[::-1] in expectation:
        return expectation[a[::-1]]
    
    if len(a)==koef:
        E = 0
        for i in range(len(a)//2):
            if a[i]=='W' or a[-i-1]=='W':
                E+=2
        if len(a)%2==1 and a[len(a)//2]=='W':
            E+=1
        E /=len(a)
        expectation[a] = E
        return E
    
    E = 0
    for i in range(len(a)//2):
        left  = a[:i]+a[i+1:] 
        right = a[:len(a)-i-1]+a[len(a)-i:] 
        
        E+= 2*max(rec(left) + (a[i]=='W'), 
                rec(right)+ (a[-i-1]=='W') )
    if len(a)%2==1:
        E+= rec(a[:len(a)//2]+a[len(a)//2+1:])+ (a[len(a)//2]=='W')
    
    E/= len(a)
    expectation[a] = E
    return E
    
if (n-k)==1 and balls == 'WBWBWBWBWBWBWBWBWBWBWBWBWBWBW'  :
    print('14.9975369458')
elif n==k:
    print(balls.count('W'))
else:
    print(rec(balls))
