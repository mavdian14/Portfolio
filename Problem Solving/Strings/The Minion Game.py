def minion_game(string):
    #score counters for kevin & stuart
    k=0
    s=0
    vowels="AaEeIiOoUu"
    for i in range(len(string)):
        if string[i] in vowels:
            k += len(string)-i
        else:
            s += len(string)-i
    
    if k>s:
        print("Kevin",k)
    elif k==s:
        print("Draw")
    else:
        print("Stuart",s)
    

