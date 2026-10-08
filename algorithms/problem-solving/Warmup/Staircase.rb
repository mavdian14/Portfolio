#!/bin/ruby

require 'json'
require 'stringio'

#
# Complete the 'staircase' function below.
#
# The function accepts INTEGER n as parameter.
#

def staircase(n)
    for i in range(1,n):
        s = "#" * i 
        print(s.rjust(n))

end

n = gets.strip.to_i

staircase n
