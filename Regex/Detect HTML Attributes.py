# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
from collections import defaultdict

#tag & attr compilers
tag_regex = re.compile(r"<(\w+).*?>")
attrs_regex = re.compile(r"\s(\w+)=")
output = defaultdict(set)

for _ in range(int(input())):
    #finditer() returns an iterr object & all matches in order of tag_regex in this case
    for i in tag_regex.finditer(input()):
        #find all iterations of attrs (which is the first group, group(0), following the tag among all iters of tag)
        attrs = attrs_regex.findall(i.group(0))
        #update adds all found attrs into the values of i.group(1) key in output dict
        output[i.group(1)].update(attrs)

for k,v in sorted(output.items()):
    print(f"{k}:{','.join(sorted(v))}")
