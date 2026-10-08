# Enter your code here. Read input from STDIN. Print output to STDOUT
import re
for _ in range(int(input())):
    u = ''.join(sorted(input()))
    # asert is used for debugging. It will continue running the argument if its True, otherwise it will raise an AssertionError when ran falsely
    try:
        #find at least 2 uppercase letters in u
        assert re.search(r'[A-Z]{2}', u)
        #find at least 3 digits in u ("\d")
        assert re.search(r'\d\d\d', u)
        #find no characters that aren't alphanumeric
        assert not re.search(r'[^a-zA-Z0-9]', u)
        #ensures no character repeats ( (.) means any character, \1 means match the first group with itself 
        assert not re.search(r'(.)\1', u)
        #make sure u is 10 characters
        assert len(u) == 10    
    except:
        print('Invalid')
    else:
        print('Valid')  
