from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
     def handle_comment(self, comment):
          if '\n' in comment:
            print('>>> Multi-line Comment')
          else:
            print('>>> Single-line Comment')
          print(comment)
        
     def handle_data(self, data):
        if data == '\n': return
        print('>>> Data')
        print(data)

html = ""
for i in range(int(input())):
    #Return a copy of the string with trailing whitespace removed.If chars is given and not None, remove characters in chars instead
    html += input().rstrip()
    html += '\n'
    
parser = MyHTMLParser()
parser.feed(html)
parser.close()
