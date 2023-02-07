def print_formatted(number):
    #largest binary number
    # .bin() returns the binary representation of an integer.
    #replace() Return a copy with all occurrences of substring old replaced by new. Count Maximum number of occurrences to replace. -1 (the default value) means replace all occurrences.
    w = len(str(bin(number)).replace('0b',''))
    
    for i in range(1,number+1):
        d = str(i).rjust(w,' ')
        o = oct(i).replace('0o','').rjust(w, ' ')
        h = hex(i).replace('0x','').upper().rjust(w, ' ')
        b = bin(i).replace('0b','').rjust(w, ' ')
        
        print(d,o,h,b)

