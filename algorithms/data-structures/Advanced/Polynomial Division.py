#!/bin/python3

import math
import os
import random
import re
import sys

# returns d, x, y so that gcd(a, b) = d and ax + by = d
def extended_euclidean_alg(a,b):
    # starts out as p[0] = P_{-1}, p[1] = P_0 and same for q
    # in general it's the previous 2 terms, P_{i-1}, P_{i-2}
    p = [0, 1]
    q = [1, 0]
    counter = 1
    while b != 0:
        quo = a//b
        rem = a % b
        newP = quo*p[1] + p[0]
        newQ = quo*q[1] + q[0]
        p[0] = p[1]
        p[1] = newP
        q[0] = q[1]
        q[1] = newQ
        a = b
        b = rem
        counter = (counter + 1) % 2
    minusOne = (counter-1) % 2
    return a, q[0]*((-1)**minusOne), p[0]*((-1)**(counter))

def leastSigBit(num):
    return (num & -num)

# implementation of a Fenwick tree
class PrefixSumTree(object):
    def __init__(self,array):
        l = len(array)
        self.sums = [0] * l
        for i in range(1,l):
            cl = i - leastSigBit(i)
            for j in range(cl+1,i+1):
                self.sums[i] = (self.sums[i] + array[j]) % p

    def sum(self,i):
        sum = 0
        while i > 0:
            sum = (sum + self.sums[i]) % p
            i -= leastSigBit(i)
        return sum

    # adds toAdd to the ith element of array
    def add(self,i,toAdd):
        while i <= len(self.sums)-1:
            self.sums[i] = (self.sums[i] + toAdd) % p
            i += leastSigBit(i)

p = 10**9 + 7

def polynomialDivision(a, b, c, queries):
    res = []
    a_inv = extended_euclidean_alg(p, a)[2]
    x = -b*a_inv % p
    # if x != 0 then we have to build the sum tree
    if x != 0:
        l = len(c)
        # polyArray[i+1] = c[i]*x^i % p and polyArray[0] = 0
        polyArray = [0] * (l+1)
        polyArray[1] = c[0]
        # powsOfX[i] = x^i % p
        powsOfX = [1] * l
        for i in range(1,l):
            newPow = (powsOfX[i-1]*x) % p
            powsOfX[i] = newPow
            polyArray[i+1] = (c[i]*newPow) % p
        sumTree = PrefixSumTree(polyArray)
    for q in queries:
        if q[0] == 1:
            # compute how much we need to add for the sum
            toAdd = q[2]-c[q[1]]
            # update the array c with our new entry q[2]
            c[q[1]] = q[2]
            if x != 0:
                # then we add the appropriate amount to our prefix sums.
                # since sumTree keeps track of sum c_i * x^i we multiply by the 
                # appropriate power of x
                sumTree.add(q[1]+1,(toAdd*(powsOfX[q[1]])) % p)
        else:
            # remember c is zero indexed but sumTree is one indexed
            # so we do sum(q[2]+1) - sum(q[1]) instead of sum(q[2]) - sum(q[1]-1)
            pOfX = c[q[1]] if x == 0 else (sumTree.sum(q[2]+1) - sumTree.sum(q[1])) % p
            if pOfX == 0:
                res.append("Yes")
            else:
                res.append("No")
    return res


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    nabq = input().split()

    n = int(nabq[0])

    a = int(nabq[1])

    b = int(nabq[2])

    q = int(nabq[3])

    c = [int(t) for t in input().rstrip().split()]

    queries = []

    for _ in range(q):
        queries.append([int(t) for t in input().rstrip().split()])

    result = polynomialDivision(a, b, c, queries)

    fptr.write('\n'.join(result))
    fptr.write('\n')

    fptr.close()
