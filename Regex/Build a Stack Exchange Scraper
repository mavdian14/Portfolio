# Enter your code here. Read input from STDIN. Print output to STDOUTfpower 
import re, sys

id_regex = re.compile(r"question-summary-(\d+)")
q_regex = re.compile(r"question-hyperlink\">(.+?)<")
date_regex = re.compile(r"relativetime\">(.*?)<")

text = sys.stdin.read()
#findall() is used to match all occurences of a match in a given pattern
for i in zip(id_regex.findall(text),q_regex.findall(text),date_regex.findall(text)):
    print(";".join(i))
