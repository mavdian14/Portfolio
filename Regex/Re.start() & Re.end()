# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
s = input()
k = input()
pattern = re.compile(k)
m = pattern.search(s)
if not m:
    print("(-1, -1)")
else:
    while m:
        print("({0}, {1})".format(m.start(), m.end()-1))
        m = pattern.search(s, m.start()+1)

# re.findall() return all the non-overlapping matches of patterns in a string as a list of strings

#re.finditer() returns an iterator yielding MatchObject instances over all non-overlapping matches for the re pattern in the string.

# re.start/end() return the indices of the start/end of the substring matched by the group
