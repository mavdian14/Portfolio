# Enter your code here. Read input from STDIN. Print output to STDOUT
import re

langs = "C:CPP:JAVA:PYTHON:PERL:PHP:RUBY:CSHARP:HASKELL:CLOJURE:BASH:SCALA:ERLANG:CLISP:LUA:BRAINFUCK:JAVASCRIPT:GO:D:OCAML:R:PASCAL:SBCL:DART:GROOVY:OBJECTIVEC".split(":")

regex = re.compile("^[1-9]\d{4} ([A-Z]+)$")

for _ in range(int(input())):
    print("VALID" if regex.match(input()).group(1) in langs else "INVALID")
