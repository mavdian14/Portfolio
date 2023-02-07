# Enter your code here. Read input from STDIN. Print output to STDOUT

import re
pattern = r"^(?P<ipv4>([\d]{1,3}\.){3}([\d]{1,3}))|(?P<ipv6>([\da-f]{1,4}\:){7}[\da-f]{1,4})$"
#.compile() is used to compile a regex pattern provided as a str into a regex object.
pattern = re.compile(pattern)

for _ in range(int(input())):
    #Scan through string looking for a match to the pattern, returning a Match object, or None if no match was found.
    r = re.search(pattern, input())
    if r:
        #extract match value of group ipv4
        if r.group("ipv4"):
            nums = [n for n in r.group("ipv4").split(".") if int(n) <= 255]
            print("IPv4" if len(nums) == 4 else "Neither")
        elif r.group("ipv6"):
            print("IPv6")
    else:
        print("Neither")
