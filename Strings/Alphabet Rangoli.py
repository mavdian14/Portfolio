import string
def print_rangoli(size):
    characters = string.ascii_lowercase
    lst = []
    width = 4 * size - 3
    for i in range(size):
        s = '-'.join(characters[i:size])
        lst.append((s[::-1] + s[1:]).center(width,'-'))
    #
    print('\n'.join(lst[:0:-1] + lst))

