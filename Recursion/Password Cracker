#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'passwordCracker' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING_ARRAY passwords
#  2. STRING loginAttempt
#

def passwordCracker(passwords, loginAttempt):
    #contains the tabulation array with the calculation answers
    tab=[None]*(len(loginAttempt)+1)
    tab[0]=""
    
    for i in range(1,len(loginAttempt)+1):
        for pwd in passwords:
            k=i-len(pwd)
            #could have been -> loginAttempt[:i].endswith(pwd)
            if loginAttempt[k:i]==pwd:
                #This check missing almost made me go crazy
                if tab[k] is not None:
                    tab[i] = f"{tab[k]} {loginAttempt[k:i]}"
                    break
    
    out=tab[-1]
    
    if out is None:
        return "WRONG PASSWORD"
    else:
        return out.strip()

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    t = int(input().strip())

    for t_itr in range(t):
        n = int(input().strip())

        passwords = input().rstrip().split()

        loginAttempt = input()

        result = passwordCracker(passwords, loginAttempt)

        fptr.write(result + '\n')

    fptr.close()
