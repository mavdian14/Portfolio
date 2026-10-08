#!/bin/python3

import math
import os
import random
import re
import sys
from collections import Counter



if __name__ == '__main__':
    s = sorted(input())
    #z = Counter(s)
    #most_common(n) returns a list of the top 'n' elements from most common to least common
    z=Counter(s).most_common(3)
    for x in z:
        print(*x)
    
