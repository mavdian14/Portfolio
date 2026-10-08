# Enter your code here. Read input from STDIN. Print output to STDOUT

#relevant package for computing angles
import math

#initialize the side length of the triangle
ab = float(input())
bc = float(input())

#find the distances
ac = math.sqrt((ab*ab)+(bc*bc))
bm = ac/2.0
mc = bm

#equalizing the sides
b = mc
c = bm
a = bc

#where b=c, find the angle in radian
angle_b_radian = math.acos(a/(2*b))

#convert radian to degree
angle_b_degree = int(round((180*angle_b_radian)/math.pi))

#printing with degree
#the '\u00B0' is the degree symbol
print(angle_b_degree, '\u00B0',sep='')


