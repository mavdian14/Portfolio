# Enter your code here. Read input from STDIN. Print output to STDOUT
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print('Start :',tag)
        for ele in attrs:
            print('->',ele[0],'>',ele[1])
    
    def handle_endtag(self, tag):
        print('End   :',tag)
    
    def handle_startendtag(self, tag, attrs):
        print('Empty :',tag)
        for ele in attrs:
            print('->',ele[0],'>',ele[1])
    
MyParser = MyHTMLParser()
#.feed() Feed data to the parser. Call this as often as you want, with as little or as much text as you want (may include '\n').
MyParser.feed(''.join([input().strip() for _ in range(int(input()))]))
        
        
